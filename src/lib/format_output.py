def format_output(images_path, output_message):  
    width = 30+15  
    print("━" * width)
    print("IMAGE", " " * 13, "┃", " " * 8, "STATUS")
    print("━" * width)
    for i in range(0, len(images_path)):
        print("{:<30} {:^15}".format(
            images_path[i][12:].replace("/", "").replace(".jpg", ""), 
            output_message[i]
        ))
    print("━" * width)
    print("\n\n")
