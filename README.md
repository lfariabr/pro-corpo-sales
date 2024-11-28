# Pró-Corpo Lab - Sales Dashboard 💜

An elegant and interactive dashboard for sales analysis at Pró-Corpo Lab, built with Streamlit and Plotly.

## ✨ Features

- **Time Analysis**: Dynamic date range filter for sales analysis
- **Key Metrics**: Quick view of important statistics
  - Total Sales Value
  - Average Ticket
  - Total Number of Sales
- **Interactive Visualizations**:
  - Sales by Unit 💜
  - Consultant Performance 💎
  - Procedure Distribution 💜
- **Responsive Design**: Modern and adaptive interface

## 🚀 Tech Stack

- **Streamlit**: Web application framework
- **Plotly**: Interactive and modern charts
- **Pandas**: Data manipulation and analysis
- **Python**: Core programming language

## 💻 Getting Started

1. Clone the repository
```bash
git clone [your-repository]
cd coc_sales
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the application
```bash
streamlit run app_excel.py
```

## 📁 Project Structure

```
coc_sales/
├── app_excel.py          # Main application
├── requirements.txt      # Project dependencies
├── .env                 # Environment variables (not versioned)
└── .gitignore          # Git ignored files
```

## 🔒 Environment Variables

Create a `.env` file in the project root with the following variables:
```
# Required environment variables
DATABASE_URL=your_url
API_KEY=your_key
```

## 🤝 Contributing

Contributions are welcome! Feel free to open issues and pull requests.

## 📝 License

This project is licensed under the [luisfaria.dev].

---

Built with 💜 by [Luis/Pró-Corpo Lab]
