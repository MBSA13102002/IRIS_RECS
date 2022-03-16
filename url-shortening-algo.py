import requests
header = {
    "Authorization":"bbf116bb1fea464e353f69668d1fedbffed3e885",
    "Content-Type": "application/json"
}
url = 'https://api-ssl.bitly.com/v4/shorten'
myobj = {
    "long_url": "https://www.w3schools.com/python/ref_requests_post.asp"
  
  
}
x = requests.post(url, json = myobj,headers=header)

print(x.link)