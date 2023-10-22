import requests, json, time, json, base64, string, random, os
from PIL import Image

# load conifg (rewrite using configparser)
config = {}
with open("config.json", 'r') as f:
    config = json.load(f)

def makeGuild(name: str) -> str:
    res = requests.post("https://canary.discord.com/api/v9/guilds", headers=config['headers'], json={"name": name})
    return json.loads(res.text)['id']

def addEmoji(path, guild_id: str, emoji_name: str) -> str:
    with open(path, "rb") as image_file:
        image_data = image_file.read()

    image_base64 = base64.b64encode(image_data)
    image_base64_string = image_base64.decode('utf-8')

    res = requests.post("https://canary.discord.com/api/v9/guilds/"+guild_id+"/emojis", headers=config['headers'], json={
        "image": "data:image/png;base64,"+image_base64_string, 
        "name": emoji_name
    })

    return res.text

def resizer(img_path): # panklav je reko da ne radim sa img path vjv jer se kopira str umjesto 2 broja
    # resize img so h = y
    original_image = Image.open(img_path)
    w, h = original_image.size

    total = w

    if h > w:
        total=h

    new_size = (total, total)
    resized_image = original_image.resize(new_size)
    resized_image.save(img_path)
    original_image.close()
    resized_image.close()

def dicectimg(img_path, file_type: str):

    resizer(img_path)

    original_image = Image.open(img_path)
    width, height = original_image.size

    subimage_width = width // 7
    subimage_height = height // 7

    small_images = []

    for y in range(7):
        for x in range(7):
            # Define the coordinates of the region to extract
            left = x * subimage_width
            upper = y * subimage_height
            right = left + subimage_width
            lower = upper + subimage_height

            # Crop and store the smaller image
            subimage = original_image.crop((left, upper, right, lower))
            small_images.append(subimage)


    for i, subimage in enumerate(small_images):
        subimage.save(f"temp/subimage_{i}."+file_type)

    original_image.close()

    return i

def validateConfig():
    if(len(config['path_img']) > 1): 
        return 0
    if(len(config['output_file']) > 1):
        return 0
    if(len(config["headers"]["authorization"]) > 1):
        return 0

    print("bad config")
    exit()

def randomemojiname(i: int) -> str: # (rewrite to use a const random base for evry emoji [add emoji msg prediction])
    i = str(i)
    return i+"_"+''.join(random.choice(string.ascii_letters) for _ in range(3))


# if config.output_file is a existing file make a new one that ends in _<number>.txt
def generate_new_filename(base_filename) -> str:
    new_filename = base_filename
    counter = 0
    while os.path.exists(new_filename):
        counter += 1
        new_filename = f"{os.path.splitext(base_filename)[0]}_{counter}.txt"
    return new_filename

def main():
    validateConfig()

    # make guild w/ random name
    guild_id = makeGuild(''.join(random.choice(string.ascii_letters) for _ in range(8)))

    if not os.path.exists("temp"):
        os.makedirs("temp")

    # get img file type
    file_type = config['path_img'].split('.')[1]

    # get num of emojis
    max = dicectimg(config['path_img'], file_type)

    copytext = ''

    # upload emojis to guild and construct msg
    for i in range(max+1):
        res = addEmoji(f"temp/subimage_{i}."+file_type, guild_id, randomemojiname(i))
        res = json.loads(res)
        copytext+=f"<:{res['name']}:{res['id']}>"

        if((i+1)%7==0):
            copytext+="\n"

        time.sleep(1)
    
    print(copytext)

    new_filename = generate_new_filename(config['output_file'])

    with open(new_filename, "w") as file:
        file.write(copytext)

if __name__ == "__main__":
    main()