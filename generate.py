import pandas as pd
import re

# Load the ASN data from the provided URL
asn_url = "https://raw.githubusercontent.com/ipverse/asn-info/master/as.csv"
asn_df = pd.read_csv(asn_url)

world_universities_url = "https://raw.githubusercontent.com/endSly/world-universities-csv/master/world-universities.csv"
world_universities_df = pd.read_csv(world_universities_url)

# Rename the columns for easier access
world_universities_df.columns = ['country_code', 'university_name', 'website']

# Drop rows where 'description' is NaN in the ASN data
asn_df = asn_df.dropna(subset=['description'])

# Define a regex pattern to identify universities, institutes, and colleges
university_pattern = re.compile(r'\b(University|Institute|College|Universitet|School)\b', re.IGNORECASE)

# Filter rows where 'description' contains the terms for universities
asn_universities_df = asn_df[asn_df['description'].str.contains(university_pattern)]

# Match by checking if the university name is part of the ASN description
matched_universities_df = asn_universities_df[
    asn_universities_df['description'].apply(lambda desc: any(univ.lower() in desc.lower() for univ in world_universities_df['university_name']))
]

# Sort by ASN in ascending order to prioritize lower ASN values
matched_universities_df = matched_universities_df.sort_values(by='asn')

# Keep only the first (highest) occurrence for each university by checking the description
matched_universities_df['university_match'] = matched_universities_df['description'].apply(
    lambda desc: next((univ for univ in world_universities_df['university_name'] if univ.lower() in desc.lower()), None)
)

# Drop duplicates based on the matched university name, keeping the first (lower ASN)
final_universities_df = matched_universities_df.drop_duplicates(subset=['university_match'])

# Add a rank column
final_universities_df['rank'] = range(1, len(final_universities_df) + 1)

# Create a hyperlink for each ASN to Cloudflare Radar
final_universities_df['asn'] = final_universities_df['asn'].apply(lambda x: f'<a href="https://radar.cloudflare.com/as{x}">{x}</a>')

# Select only the needed columns and reorder them (rank, Description, ASN, Handle)
final_df = final_universities_df[['rank', 'description', 'asn', 'handle']]

# Generate HTML table with ASN hyperlinks
html_table = final_df.to_html(index=False, escape=False)

# Add title and GitHub link
title = "<h1>University ASN Ranking</h1>"
github_link = '<p><a href="https://github.com/sebersta/University-ASN-Ranking">GitHub</a></p>'

# Combine everything into the final HTML content
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>University ASN Ranking</title>
</head>
<body>
    {title}
    {html_table}
    {github_link}
    <p>Source: <a href="{asn_url}">ASN Data</a></p>
    <p>Source: <a href="{world_universities_url}">World Universities Data</a></p>
</body>
</html>
"""

# Save the HTML content to a file
with open("index.html", "w") as file:
    file.write(html_content)

