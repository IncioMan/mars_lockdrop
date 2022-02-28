mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
[theme]\n\
primaryColor=\"#001a33\"\n\
backgroundColor=\"#001a33\"\n\
secondaryBackgroundColor=\"#122647\"\n\
textColor=\"#FFFFFF\"\n\
font=\"sans serif\"\n\
\n\
" > ~/.streamlit/config.toml