while true; do
    pipenv run python scripts/phase2.py 
    git add data/*
    git commit -m 'new data'
    git push
done