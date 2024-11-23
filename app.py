import streamlit as st
import requests
from bs4 import BeautifulSoup
import re

# Function to scrape equations from the Wikipedia page
def get_equations(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        equations = []
        for math_tag in soup.find_all("math"):
            equation = math_tag.text.strip()
            equation = preprocess_equation(equation)  # Preprocess equations
            equations.append(equation)
        return equations
    except Exception as e:
        st.error(f"Error fetching equations: {e}")
        return []

# Preprocess equations to clean and standardize LaTeX
def preprocess_equation(equation):
    # Replace Unicode variables with LaTeX equivalents
    equation = equation.replace("β", r"\beta").replace("ε", r"\epsilon").replace("ϵ", r"\varepsilon")
    # Remove unnecessary macros
    equation = re.sub(r"\\displaystyle", "", equation)
    equation = re.sub(r"\\boldsymbol", "", equation)
    return equation

# Function to apply colors to specified variables
def colorize_variables(equation, color_map):
    def replacer(match):
        decoration = match.group(1) or ""  # Match optional decorations (e.g., \hat, \bar)
        variable = match.group(2)  # Match the variable
        subscript = match.group(3) or ""  # Match optional subscript/superscript
        full_variable = decoration + variable  # Combine decoration with the variable

        # Check if the full variable (e.g., \hat{\beta}) exists in color_map
        if full_variable in color_map:
            return rf"\textcolor{{{color_map[full_variable]}}}{{{decoration}{variable}}}{subscript}"
        elif variable in color_map:  # Check if base variable exists in color_map
            return rf"\textcolor{{{color_map[variable]}}}{{{decoration}{variable}}}{subscript}"
        else:
            return match.group(0)  # Return the original match if no color mapping

    # Regex to match variables with optional decorations and subscripts/superscripts
    pattern = r"(\\(?:hat|bar|tilde|dot|ddot|vec|underline)?)?(\\?[a-zA-Z]+)([_^{][a-zA-Z0-9]+)?"
    return re.sub(pattern, replacer, equation)

# Streamlit App
st.title("Dynamic Equation Highlighter from Wikipedia")

# URL Input
url = st.text_input("Enter Wikipedia URL for equations:", "https://en.wikipedia.org/wiki/Ordinary_least_squares")

if url:
    # Fetch equations
    equations = get_equations(url)
    
    if equations:
        st.success(f"Found {len(equations)} equations on the page.")

        # Sidebar for color options
        st.sidebar.title("Customize Variable Colors")
        x_color = st.sidebar.color_picker("Choose color for x:", "#FF0000")
        y_color = st.sidebar.color_picker("Choose color for y:", "#00FF00")
        b_color = st.sidebar.color_picker("Choose color for β (beta):", "#0000FF")
        e_color = st.sidebar.color_picker("Choose color for ε (epsilon):", "#800080")

        # Map variables to colors
        color_map = {
            "x": x_color,
            "y": y_color,
            r"\beta": b_color,
            r"\epsilon": e_color,      # Standard LaTeX epsilon
            r"\varepsilon": e_color,  # Rounded epsilon
            r"ϵ": e_color,            # Unicode epsilon
            r"\hat{y}": y_color,      # Optional: explicitly color decorated variables
            r"\hat{\beta}": b_color,
        }

        # Initialize session state for navigation
        if "equation_index" not in st.session_state:
            st.session_state.equation_index = 0

        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Previous"):
                st.session_state.equation_index = max(0, st.session_state.equation_index - 1)
        with col2:
            if st.button("Next"):
                st.session_state.equation_index = min(len(equations) - 1, st.session_state.equation_index + 1)

        # Display the current equation
        current_equation = equations[st.session_state.equation_index]

        st.markdown(f"### Equation {st.session_state.equation_index + 1}")
        # Original Equation (without color)
        st.markdown("**Original:**")
        st.latex(current_equation)

        # Colored Equation (with dynamic color)
        st.markdown("**With Color:**")
        colored_equation = colorize_variables(current_equation, color_map)
        st.latex(colored_equation)

        # Footer with current equation index and total
        st.markdown(
            f"**Equation {st.session_state.equation_index + 1} of {len(equations)}**"
        )
    else:
        st.warning("No equations found on the page. Please check the URL or try another page.")
