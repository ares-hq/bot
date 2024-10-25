import requests

# Define the API endpoint
url = "https://api.ftcscout.org/graphql"

# Define the GraphQL query
query = """
query{
  teamByNumber(number: 14584) {
    name
  }
}
"""

# Set up the request headers, including the content type
headers = {
    "Content-Type": "application/json"
}

# Send the POST request to the API with the query
response = requests.post(url, json={'query': query}, headers=headers)

# Check for errors and print the results
if response.status_code == 200:
    data = response.json()
    print("Response Data:", data)
else:
    print("Failed to fetch data. Status code:", response.status_code)
    print("Error details:", response.text)