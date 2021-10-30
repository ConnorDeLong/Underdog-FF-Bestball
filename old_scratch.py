import requests

headers = {
    'authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiIwOGQxMmUxNC0xMmY0LTRiZWYtYWE1Mi0zZmUzZmY2YjdlNDUiLCJzdWIiOiIwMzcxNzEzMS1lMDUzLTQ1MWQtOWJlNi0wOTc1NWY1ODc1YWUiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MzU2MjE2ODUsImV4cCI6MTYzODI1MTQzMX0.xHCZIgQR9XuyPpiU3Bf5mtZGtzMIarmehvnt3A7Qro0',
}

response = requests.get('https://api.underdogfantasy.com/v2/drafts/f75ed573-6a11-4e59-b712-1e8826d05c44', headers=headers)

print(response)




