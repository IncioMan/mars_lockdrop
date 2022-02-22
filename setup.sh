mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
port = $PORT\n\
enableCORS = false\n\
[theme]\n\
primaryColor=\"#282e53\"\n\
backgroundColor=\"#282e53\"\n\
secondaryBackgroundColor=\"#4E527A\"\n\
textColor=\"#FFFFFF\"\n\
font=\"sans serif\"\n\
\n\
" > ~/.streamlit/config.toml