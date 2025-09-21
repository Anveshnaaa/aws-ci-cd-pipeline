import boto3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# Initialize the S3 client
s3 = boto3.client('s3')

def lambda_handler(event, context):
    # S3 bucket details
    input_bucket_name = "movie-s3-1"
    input_file_key = "top_movies.csv"
    output_bucket_name = "movie-visualizations-output"

    try:
        # Download the CSV file from the input bucket
        df = load_csv_from_s3(input_bucket_name, input_file_key)

        # Ensure required columns are present
        required_columns = ['Title', 'Budget', 'Revenue', 'Genre', 'Popularity', 'Production Companies']
        check_required_columns(df, required_columns)

        # Remove duplicate movies based on 'Title'
        df = df.drop_duplicates(subset='Title')

        # 1. Budget vs Revenue
        create_budget_vs_revenue_chart(df, output_bucket_name)

        # 2. Genre vs Average Popularity
        create_genre_vs_popularity_chart(df, output_bucket_name)

        # 3. Popularity vs Production Houses
        create_popularity_vs_production_houses_chart(df, output_bucket_name)

        return {
            'statusCode': 200,
            'body': 'Visualizations created and uploaded successfully.'
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'errorMessage': str(e)
        }

def load_csv_from_s3(bucket_name, file_key):
    """Load CSV content from an S3 bucket into a Pandas DataFrame."""
    response = s3.get_object(Bucket=bucket_name, Key=file_key)
    csv_content = response['Body'].read().decode('utf-8')
    return pd.read_csv(io.StringIO(csv_content))

def check_required_columns(df, required_columns):
    """Ensure the DataFrame has all required columns."""
    for col in required_columns:
        if col not in df.columns:
            raise KeyError(f"Missing required column: {col}")

def create_budget_vs_revenue_chart(df, output_bucket_name):
    """Create and upload the Budget vs Revenue chart."""
    df_budget_revenue = df[['Title', 'Budget', 'Revenue']].dropna()
    df_budget_revenue = df_budget_revenue[df_budget_revenue['Budget'] > 0]
    df_budget_revenue = df_budget_revenue.sort_values(by='Budget', ascending=False).head(10)

    titles = df_budget_revenue['Title']
    budgets = df_budget_revenue['Budget']
    revenues = df_budget_revenue['Revenue']

    x = range(len(titles))
    plt.figure(figsize=(14, 8))
    bar_width = 0.35

    plt.bar(x, budgets, width=bar_width, label='Budget', color='lightblue', alpha=0.8)
    plt.bar([i + bar_width for i in x], revenues, width=bar_width, label='Revenue', color='darkblue', alpha=0.8)

    for i, v in enumerate(budgets):
        plt.text(i, v + max(budgets) * 0.02, f"${v:,}", ha='center', va='bottom', fontsize=10, color='black')
    for i, v in enumerate(revenues):
        plt.text(i + bar_width, v + max(revenues) * 0.02, f"${v:,}", ha='center', va='bottom', fontsize=10, color='black')

    plt.xlabel('Movies', fontsize=12)
    plt.ylabel('Amount (in USD)', fontsize=12)
    plt.title('Budget vs Revenue (Top 10 Movies)', fontsize=16)
    plt.xticks([i + bar_width / 2 for i in x], titles, rotation=45, ha='right', fontsize=10)
    plt.legend()
    plt.tight_layout(pad=2)  # Ensures layout fits within the figure

    save_plot_to_s3(output_bucket_name, 'budget_vs_revenue_vertical_bar.png')

def create_genre_vs_popularity_chart(df, output_bucket_name):
    """Create and upload the Genre vs Average Popularity chart."""
    genre_popularity_avg = df.groupby('Genre')['Popularity'].mean().sort_values()
    plt.figure(figsize=(14, 20))
    genre_popularity_avg.plot(kind='bar', color='blue', alpha=0.7)
    plt.title('Genre vs Average Popularity', fontsize=16)
    plt.xlabel('Genre', fontsize=12)
    plt.ylabel('Average Popularity', fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout(pad=2)  # Ensures layout fits within the figure

    save_plot_to_s3(output_bucket_name, 'genre_vs_avg_popularity.png')

def create_popularity_vs_production_houses_chart(df, output_bucket_name):
    """Create and upload the Popularity vs Production Houses chart."""
    production_popularity = df[['Production Companies', 'Popularity']].dropna()
    production_popularity = production_popularity.groupby('Production Companies')['Popularity'].mean()
    production_popularity = production_popularity.sort_values(ascending=False).head(10)

    plt.figure(figsize=(14, 10))  # Larger figure for longer labels
    sns.barplot(
        x=production_popularity.values,
        y=production_popularity.index,
        palette="Blues_r"
    )
    plt.title('Popularity vs Production Houses (Top 10)', fontsize=16)
    plt.xlabel('Average Popularity', fontsize=12)
    plt.ylabel('Production Houses', fontsize=12)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout(pad=2)  # Ensures layout fits within the figure

    save_plot_to_s3(output_bucket_name, 'popularity_vs_production_houses.png')

def save_plot_to_s3(bucket_name, file_name):
    """Save the current Matplotlib plot to an S3 bucket."""
    img_data = io.BytesIO()
    plt.savefig(img_data, format='png', bbox_inches='tight')  # 'bbox_inches' ensures content is fully captured
    img_data.seek(0)
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=img_data, ContentType='image/png')
    plt.close()
