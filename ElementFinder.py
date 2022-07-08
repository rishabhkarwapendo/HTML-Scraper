#run this file after you have run HTMLScraper
import glob
import os
import pandas as pd

def findElement(dir, tag, depth, attributes_type, attributes_name, text, contains, tag_names, tag_depths, tag_texts, tag_attributes, tag_full_tag):
    tags_ret, depths_ret, texts_ret, attributes_ret, full_tags_ret = [], [], [], [], []
    full_attribute = attributes_type + '=' + attributes_name
    for i in range(len(tag_names)):
        if ((tag == '' or tag == str(tag_names[i])) and (depth == '' or depth == str(tag_depths[i])) and ((attributes_type == '' and attributes_name == '') or (full_attribute in tag_attributes[i])) 
            and (text == '' or text in str(tag_texts[i])) and (contains == '' or contains in str(tag_full_tag[i]))):
            tags_ret.append(tag_names[i])
            depths_ret.append(tag_depths[i])
            texts_ret.append(tag_texts[i])
            attributes_ret.append(tag_attributes[i])
            full_tags_ret.append(tag_full_tag[i])
    if tag == '':
        tag = 'all'
    if depth == '':
        depth = 'all'
    if text == '':
        text = 'all'
    if attributes_name == '' and attributes_type == '':
        full_attribute = 'all'
    if contains == '':
        contains = 'all'
    matched_data = {'Tag: ' + tag: tags_ret, 'Depth: ' + depth: depths_ret, 'Inner Text: ' + text: texts_ret, 
        'Attribute: ' + full_attribute: attributes_ret, 'Full Tag: ' + contains: full_tags_ret}
    df = pd.DataFrame(matched_data)
    outname = 'elements_searched.csv'
    fullname = os.path.join(dir, outname)
    df.to_csv(fullname, encoding='utf-8', header=True, index=False)


#get the folder where the regex search needs to be done
folder = input("Enter the folder name of your data: ")
dir = os.getcwd() + "/" + folder
attribute_file = glob.glob(os.path.join(dir, "all_element_data.csv"))
df = pd.read_csv(attribute_file[0])
tag_names = df.Name
tag_numbers = df.Number
tag_depths = df.Depth
tag_texts = df.Text
tag_attributes = df.Attributes
tag_full_tag = df.Full_Tag
#continue search until user wants to quit
while True:
    tags = input("""Enter the tag name (Press 'Enter' for all tags or 'q' to quit): """)
    if tags == 'q':
        break
    depths = input("""Enter the tag depth (Press 'Enter' for all depths): """)
    attributes_types = input("""Enter the attribute type (Press 'Enter' for all attribute types): """)
    attributes_names = input("""Enter the attribute name (Press 'Enter' for all attribute names): """)
    texts = input("""Enter inner text the tag should contain (Press 'Enter' for all inner text): """)   
    contains = input("""Enter any text the tag should contain (Press 'Enter' for all text): """)

    findElement(dir, tags, depths, attributes_types , attributes_names, texts, contains, tag_names, tag_depths, tag_texts, tag_attributes, tag_full_tag)