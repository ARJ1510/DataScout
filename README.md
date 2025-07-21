# DataScout 🎯
Your buddy for analytics.

DataScout is an interactive web application built with Streamlit that empowers users to clean, analyze, and chat with their data. It uses AI to generate custom cleaning plans and provides rich, interactive visualizations to uncover insights effortlessly.

-----

## Key Features

  * **🤖 AI-Powered Cleaning**: Automatically generates a data cleaning plan from an LLM tailored to your dataset.
  * **📊 Interactive EDA**: Explore your data with interactive charts for categorical distributions, numerical histograms, and correlation analysis.
  * **💬 Q\&A with Your Data**: Ask questions in plain English and get AI-generated answers based on your data.
  * **📥 Downloadable Assets**: Download the cleaned dataset as a CSV and save plots as high-quality PNG images.
  * **📁 Multi-File Support**: Works seamlessly with CSV and Excel files.

-----

## Getting Started

Follow these instructions to set up and run a local copy of DataScout.

### Prerequisites

  * Python 3.8+
  * Git

### Installation

1.  **Clone the repository:**

    ```sh
    git clone https://github.com/your-username/DataScout.git
    ```

2.  **Navigate to the project directory:**

    ```sh
    cd DataScout
    ```

3.  **Install the required dependencies:**

    ```sh
    pip install -r requirements.txt
    ```

4.  **Set up your API Key:**

      * Create a folder named `.streamlit` in the project's root directory.
      * Inside the `.streamlit` folder, create a file named `secrets.toml`.
      * Add your Together AI API key to this file:
        ```toml
        TOGETHER_API_KEY = "your_api_key_here"
        ```

### Running the App

Launch the Streamlit application by running the following command in your terminal:

```sh
streamlit run main.py
```

-----

## Usage

1.  Launch the app and wait for it to load in your browser.
2.  Upload your CSV or Excel file using the file uploader.
3.  Review the AI-generated cleaning plan and the cleaned data preview.
4.  Explore your data using the interactive dropdowns in the "Visual Analysis" section.
5.  Ask questions about your data in the "Ask AI about your data" section to get quick insights.

-----

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

-----

## License

Distributed under the MIT License. See `LICENSE` for more information.
