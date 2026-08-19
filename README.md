# Tracy Vo — Data Science Portfolio

Portfolio website hosted on GitHub Pages.

## Live site
https://YOUR_USERNAME.github.io/portfolio

## How to deploy
1. Push this folder to a GitHub repo named `portfolio`
2. Go to Settings > Pages > Source: Deploy from branch `main`, folder `/root`
3. Site is live in ~60 seconds

## How to add a new project

### Add a card to the HTML
Open `index.html` and find the comment:
- `<!-- ── ADD NEW POWER BI PROJECT: copy one <div class="card"> block ── -->`
- `<!-- ── ADD NEW PYTHON PROJECT: copy one <div class="card"> block ── -->`
- `<!-- ── ADD NEW DSA PROJECT: copy one <div class="card"> block ── -->`

Copy the nearest card block and update the title, tags, description and link.

### Add a screenshot (optional but recommended)
1. Export a screenshot of your dashboard as PNG
2. Save to `assets/screenshots/your-project-name.png`
3. In the card, replace the placeholder div with:
   `<img src="assets/screenshots/your-project-name.png" alt="Your project">`

### Update the GitHub link
Replace `YOUR_USERNAME` with your actual GitHub username in all `href` attributes.

## File structure
```
portfolio/
├── index.html              ← main site (edit this)
├── README.md
└── assets/
    ├── screenshots/        ← put PNG screenshots here
    └── pdfs/               ← put PDF reports here
```

## Project repos structure (separate repos or folders)
```
atliq-hotels/
├── AtliQ_Hotels_Dashboard.pbix
├── AtliQ_Hotels_Analysis_Report.pdf
└── README.md

freshmart/
├── FreshMart_Dashboard.pbix
└── README.md

bleve-explosion/
├── main.ipynb
└── README.md

hospital-dsa/
├── main.ipynb
├── module1file.py
├── module2file.py
├── module3file.py
├── module4file.py
└── README.md
```
