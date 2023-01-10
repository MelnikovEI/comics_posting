# Comics publisher

Script posts one random comics from [xkcd.com](https://xkcd.com/) to VK community.

### Prerequisites
1. Create a [community in VK](https://vk.com/groups?tab=admin) and [get your GROUP_ID](https://regvk.com/id/)
2. Create an [app in VK](https://vk.com/apps?act=manage)
   - Then press "manage" on your app and you'll see the "client_id" at the end of URL:
     https://vk.com/editapp?id= `11111111`
3. Get your access_token, using [Implicit Flow](https://vk.com/dev/implicit_flow_user) procedure.
   
   Do not use parameter redirect_uri in request.
   
   Parameter scope: scope=photos,groups,wall,offline.

4. Create environment variables in "your_project_folder\\ .env" file:
- VK_GROUP_ID= group_id from p.1 above.
- VK_CLIENT_ID= client_id from p.2 above.
- VK_ACCESS_TOKEN= access_token from p.3 above.
   
5. Python3 should be already installed.

   Then use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```
-> packages, listed in requirements, should be successfully installed. 

### Usage

Run the script:

```
python main.py
```

## Authors
* [Evgeny Melnikov](https://github.com/MelnikovEI)
## Acknowledgments
* Inspired by [Devman](https://dvmn.org/)
