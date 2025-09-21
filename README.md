Project Report: Automating Movie Data Processing and Visualization Using AWS
Project Objective
This project creates an automated system that fetches, processes and visualizes movie data using AWS Lambda functions. This system uses The Movie Database (TMDb) API to get data, AWS S3, CloudWatch and various layers in Lambda for data processing libraries. The project is designed to process movie data for a specific year that the user inputs, store it in a CSV format, and generate insightful visualizations, all within a serverless architecture.


Deployment Details
1.	Lambda Setup:
- Created two Lambda functions (fetch-movie-data and testPlotting39) in the AWS Management Console.
2.	Custom Layer Creation:
-	Used Docker to package pandas, matplotlib, and seaborn into a zip file.
-	Deployed the layer to Lambda and attached it to testPlotting39.
3.	CloudWatch Logging:
- Enabled logging for both functions to monitor execution and debug errors.
- Verified logs to ensure data integrity and successful visualization generation.
4.	S3 Buckets:
-	movie-s3-1: Stores the processed CSV file.
-	movie-visualizations-output: Stores the generated visualization files.
5.	IAM Role Configuration:
o	Created a role with the following policies: 
-	AmazonS3FullAccess for S3 operations.
-	AWSLambdaBasicExecutionRole for logging.



Step 1: Fetching Movie Data
Lambda Function: fetch-movie-data
This function connects to The Movie Database (TMDb) API to get information related to  movies based on whatever parameters the API has, organizes it into a proper and structured CSV format, and later saves it in an Amazon S3 bucket called movie-s3-1.  This function is designed in such a way that it works with any year that we get as input from user.

Key Features of fetch-movie-data:

-Data Fetching: Connects to TMDb API to retrieve genre information and movie details for a specified year.
Handles pagination to ensure a minimum of 30 movies are fetched.
-Data Cleaning and Processing:Removes duplicate movies based on unique identifiers.
Collects details such as title, release date, genre, budget, revenue, popularity, and production companies.
-CSV Generation:Formats the data into a CSV file for ease of use.
Stores the file in the S3 bucket movie-s3-1.
-AWS Permissions:IAM role permissions to access the TMDb API and the S3 bucket for reading and writing files.
-Permissions granted: s3:GetObject, s3:PutObject, and s3:ListBucket.
Example Usage:
Input: Year (e.g., 2023).
Output: CSV file (top_movies.csv) stored in the S3 bucket.


Code Highlights:
The function uses Python’s urllib.request to fetch data from the API as most of the others will have to be deployed to layers first.
The processed data is saved locally in /tmp/ before uploading to S3.	Added few lines of exception handling to ensure an error reporting helped me during the building procedure to find the reasons I was getting stuck.

Testing:
•	Tested locally with jupyter notebook with small data set
•	Verified CSV file the S3 bucket by making a manual visualisation in tableau as well.
<img width="345" height="207" alt="image" src="https://github.com/user-attachments/assets/261d2a2a-fe7d-4ff0-aacd-c87c14ba2019" />
<img width="344" height="206" alt="image" src="https://github.com/user-attachments/assets/4f293fd5-f9ab-4084-8f6a-cca698076bea" />


Step 2: Generating Visualizations
Visualizations Created:
1.	Budget vs Revenue: A vertical bar graph showing the top 10 movies by budget, with separate bars for budget and revenue.
2.	Genre vs Average Popularity: A bar graph displaying the average popularity of movies by genre.
3.	Popularity vs Production Houses: A horizontal bar graph showcasing the top 10 production houses based on average popularity. Lambda Function: testPlotting39
This Lambda function reads the top_movies.csv file from the movie-s3-1 bucket, generates visualizations, and saves them in another S3 bucket called movie-visualizations-output.
Key Features of testPlotting39:
1.	Reading Data:
-	Reads the CSV file from the S3 bucket into a Pandas DataFrame.
-	Ensures all required columns are present before processing.

2.	Visualization Generation:
-Budget vs Revenue: A vertical bar graph showing the top 10 movies by budget, with light blue and dark blue bars for budget and revenue, respectively.
-Genre vs Average Popularity: A bar graph displaying the average popularity of movies by genre.
-Popularity vs Production Houses: A horizontal bar graph highlighting the top 10 production houses based on average popularity, using a gradient blue palette for aesthetics.

3.	Libraries and Layers:
-Used matplotlib, pandas, and seaborn for data visualization.
-Added these libraries as a custom Lambda layer by creating a deployment package using Docker.

5.	AWS Permissions:
-IAM role permissions to read from movie-s3-1 and write to movie-visualizations-output.
-Permissions granted: s3:GetObject, s3:PutObject, and s3:ListBucket.

Example Output:
•	Visualizations saved as PNG files: 
o	budget_vs_revenue_vertical_bar.png
o	genre_vs_avg_popularity.png
o	popularity_vs_production_houses.png
<img width="468" height="617" alt="image" src="https://github.com/user-attachments/assets/4c39763c-4c7f-4b1b-b352-146e6e3dee47" />
<img width="348" height="209" alt="image" src="https://github.com/user-attachments/assets/aafbc24a-66b4-4d9b-a61e-305241c66a8c" />
<img width="344" height="206" alt="image" src="https://github.com/user-attachments/assets/6b40d999-60e2-4c3b-ac1f-bf2f45444149" />
<img width="344" height="206" alt="image" src="https://github.com/user-attachments/assets/f7636325-ecc1-4184-90c7-80212f4a26bf" />

Challenges and Solutions
1.	Missing Python Libraries:
	AWS Lambda does not include pandas and seaborn by default. 
Solution: Used Docker, Kali Linux to create a custom layer for required dependencies.
2.	Data Integrity:
Combination of some parameters were overlapping and giving invalid visualisations, thus had to ensured that duplicates were removed, and essential fields were validated. E.g. Problems that raised with the Genre parameter.
3.	Visualization Clarity:
	Since visualisations are in png format the layout adjustments were problematic to ensure that there is no clipping in images.
 
Conclusion
It automates fetching processing and visualizing movies data by means of serverless architecture making it very much scalable and cost-effective. The data is stored securely using AWS S3. The visualizations can now be used for further analysing in Tableau or embedded into dashboards for business insights.

 
Future Scope
1.	We can extend functionality to analyse a more detailed data set with another API and with TV shows or other media types.
2.	We can add user inputs for custom visualization parameters such as labels when one hovers. 
3.	Using QuickSight for better visualisations.
<img width="451" height="487" alt="image" src="https://github.com/user-attachments/assets/8fb66ed4-9a3c-4d4a-a416-c9354ac91c4c" />








