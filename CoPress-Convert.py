#!/usr/bin/env python
# encoding: utf-8
"""
convert.py

Created by Miles Skorpen on 2009-07-01
Maintained by Daniel Bachhuber, danielbachhuber@gmail.com
Contributed to by Albert Sun, Will Davis, Max Cutler
Version 1.1a
Copyright (c) 2010 CoPress
Released under GNU General Public License, version 2 (that's what WordPress uses!)

@todo Add mad comments to to the script
@todo Abstract settings/options to be read from top of file or a separate file instead of prompting every time
@todo Make the output size customizable

"""
import csv
import time
from datetime import datetime
import os
import sys
from pprint import pprint
import ConfigParser

# Helps to replace characters
def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text

class Post:
    """A Post Object converts into an item in a WordPress eXtended RSS (WXR) File through the get_item() method."""
    def __init__(self,post_id,categories,user_name,post_date,post_content,post_title,post_excerpt,identification_num):  
        self.identification_num = identification_num

        date = self.convertDate(post_date)
        self.title = post_title
        self.link  = ""
        self.pubDate = date
        user_name = user_name.split('/')
        self.creator = user_name[0] # Full Username

        self.categories = categories #list of Category objects

        #self.category = category_name
        #self.category_domain = "category"
        #self.category_nicename = "".join(char for char in category_name if char.isalpha())
        #self.category_data = category_name

        self.guid = ""
        self.guid_is_permalink = "false"
        self.description = "A post imported by CoPress Convert."
        self.content_encoded = post_content
        self.excerpt_encoded = post_excerpt

        self.wp_post_id = post_id
        self.wp_post_date = date
        self.wp_post_date_gmt = date
        self.wp_comment_status = "open"
        self.wp_ping_status = "open"
        reps = {' ':'-', '.':'', ':':'', '&amp;':'', ',':'', '&':'-', '\'':'', '"':'', '$':'', '#':'', '!':'', '@':'-', '%':'', ';':'', '?':'', '--':'-', '---':'-'}
        self.wp_post_name = replace_all(post_title, reps).lower()
        # self.wp_post_name = "".join(char for char in post_name_string if char.isalnum())
        self.wp_status = "publish"
        self.wp_post_parent = "0"
        self.wp_menu_order = "0"
        self.wp_post_type = "post"
        self.wp_post_password = ""

        self.image_custom = False
        self.image_field = []
        self.image_credit = []

    # Adds image path and credit values to beginning of a post or the Post object
    def addImage(self,path,caption,credit,settings):
        if not path.startswith('/'):
            path = '/' + path
        path = settings['prepend_image_file_path'] + path
        if settings['image_association'] == 'custom field':
            self.image_custom = True
            new_image = {}
            new_image['path'] = path
            new_image['caption'] = caption
            new_image['credit'] = credit
            self.image_field.append(new_image)
        if settings['image_association'] == 'insert':
            imageDiv = """<div class="image-wrap"><img src="%s" />%s</div>""" % (path,credit)
            self.content_encoded = imageDiv + self.content_encoded

    def convertDate(self,datestring):
        try:
            converted_date = datetime.strptime(datestring,"%b %d %Y %I:%M%p")
            return converted_date
        except:
            try:
                converted_date = datetime.strptime(datestring,"%A, %B %d, %Y")
                return converted_date
            except:
                try:
                    converted_date = datetime.strptime(datestring,"%b %d, %Y %I:%M %p")
                    return converted_date                    
                except:
                    try:
                        converted_date = datetime.strptime(datestring,"%b %d, %Y %I:%M %p")
                        return converted_date
                    except:
                        try:
                            converted_date = datetime.strptime(datestring,"%Y-%m-%d %H:%M:%S")
                            return converted_date
                        except:
                             try:
                                 converted_date = datetime.strptime(datestring,"%b %d %Y %I:%M%p")
                                 return converted_date
                             except:
                                  try:
                                      print "Attempting to process Unix time."
                                      datestring = float(datestring)
                                      converted_date = datetime.fromtimestamp(datestring) # Converting Unix time
                                      return converted_date
                                  except:
                                        print "ERROR PROCESSING DATE"
                                        print datestring + " does not match any of our possible date formats."

    def checkID(self,identification_num):
        return self.identification_num == identification_num

    def get_item(self,settings):
        creator = self.creator
        if settings['author_association'] == 'custom field':
            creator = "publicationarchive"
        if creator == "":
            creator = "publicationarchive"

        item = """
                <item>
                    <title>%s</title>
                    <link>%s</link>
                    <pubDate>%s</pubDate>
                    <dc:creator><![CDATA[%s]]></dc:creator>
                    %s
                    <guid isPermaLink="%s">%s</guid>
                    <description>%s</description>
                    <content:encoded><![CDATA[%s]]></content:encoded>
                    <excerpt:encoded><![CDATA[%s]]></excerpt:encoded>
                    <wp:post_id>%s</wp:post_id>
                    <wp:post_date>%s</wp:post_date>
                    <wp:post_date_gmt>%s</wp:post_date_gmt>
                    <wp:comment_status>%s</wp:comment_status>
                    <wp:ping_status>%s</wp:ping_status>
                    <wp:post_name>%s</wp:post_name>
                    <wp:status>%s</wp:status>
                    <wp:post_parent>%s</wp:post_parent>
                    <wp:menu_order>%s</wp:menu_order>
                    <wp:post_type>%s</wp:post_type>
                    <wp:post_password>%s</wp:post_password>
                    <wp:postmeta>
                        <wp:meta_key>_cc_article_id</wp:meta_key>
                        <wp:meta_value>%s</wp:meta_value>
                    </wp:postmeta>
                """ % ( self.title,
                        self.link,
                        self.pubDate,
                        creator,
                        "\r\n".join(cat.get_postitem() for cat in self.categories),
                        self.guid_is_permalink,
                        self.guid,
                        self.description,
                        self.content_encoded,
                        self.excerpt_encoded,
                        self.wp_post_id,
                        self.wp_post_date,
                        self.wp_post_date_gmt,
                        self.wp_comment_status,
                        self.wp_ping_status,
                        self.wp_post_name,
                        self.wp_status,
                        self.wp_post_parent,
                        self.wp_menu_order,
                        self.wp_post_type,
                        self.wp_post_password,
                        self.identification_num )
        if settings['author_association'] == 'custom field':
            addendum = """
                    <wp:postmeta>
                        <wp:meta_key>%s</wp:meta_key>
                        <wp:meta_value>%s</wp:meta_value>
                    </wp:postmeta>
            """ % (settings['author_custom_field'], self.creator)
            item = item + addendum
            
        if self.image_custom:
            for image in self.image_field:
                addendum = """
                        <wp:postmeta>
                            <wp:meta_key>%s</wp:meta_key>
                            <wp:meta_value>%s</wp:meta_value>
                        </wp:postmeta>
                """ % (settings['image_custom_field'], image['path']+'{}'+image['caption']+'{}'+image['credit'])
                item = item + addendum

        ending = """
                </item>
        """
        item = item + ending

        return item

class Category:
    def __init__(self,category_name):   # Category and User should be objects        
        self.category_name = category_name
        self.category_parent = ""
        self.category_nicename = "".join(char for char in category_name if char.isalpha())
         
    def get_name(self):
        return self.category_name
               
    def get_item(self):
        item = """
                <wp:category>
                    <wp:category_nicename>%s</wp:category_nicename>
                    <wp:category_parent>%s</wp:category_parent>
                    <wp:cat_name><![CDATA[%s]]></wp:cat_name>
                </wp:category>
                """ % ( self.category_nicename,
                        self.category_parent,
                        self.category_name )     
        return item
    def get_postitem(self):
        item = """
                <category><![CDATA[%s]]></category>
                <category domain="%s" nicename="%s"><![CDATA[%s]]></category>
                """ % ( self.category_name, "category", self.category_nicename, self.category_name )
        return item

def custom(database): #ONLY USED FOR CUSTOM DATABASES
    PostList = []
    CategoryList = []

    print "This script will create a WordPress eXtended RSS file."
    print "You can merge it with your existing site easily."
    #print "We'll first need to know which rows in the CSV file correspond with certain data points. You can manually add these in the "
    #print "If your data doesn't have a certain column, please enter 'None'."

    # DO YOU WANT TO SET THE VARIABLES?

    story_id = -1
    story_date = -1
    category_id = -1
    story_title = -1
    story_summary = -1
    story_text = -1
    story_author = -1

    trans_filename = raw_input("To translate section and category IDs to names, enter the name of a translation file: ")

    if database == "joomla":

        #print "Print your JOS_Content table into a CSV. Open it up in excel, and delete every column except ..."
        #print " id,title,introtext,fulltext,cat_id,created,created_by_alias. Keep them in that order."
        print "Format your content as CSV with the following headers: "
        print "id,title,introtext,fulltext,sectionid,catid,created,created_by,created_by_alias"

        if trans_filename:
            #build a dict to translate id's to category names
            trans_reader = csv.reader(open(trans_filename), delimiter=',', quotechar='"')
            headerl = trans_reader.next()
            trans = {}
            trans[headerl[0]] = {}
            trans[headerl[1]] = {}
            for line in trans_reader:
                if line[0]:
                    trans[headerl[0]][line[0]] = line[2]
                if line[1]:
                    trans[headerl[1]][line[1]] = line[2]

        story_id = 0
        story_date = 6
        section_id = 4
        category_id = 5
        story_title = 1
        story_summary = 2
        story_text = 3
        story_author = 8

    if story_id == -1:
       move_on = False
       while move_on == False:
        story_id = raw_input("Story ID Number:")
        story_date = raw_input("Story Date: ")
        category_id = raw_input("Story Category: ")
        story_title = raw_input("Story Headline: ")
        story_summary = raw_input("Story Summary: ")
        story_text = raw_input("Story Text: ")
        story_author = raw_input("Story Author: ")

        print "You just set the variables as: "
        print """
        story_id = %s
        story_date = %s
        category_id = %s
        story_title = %s
        story_summary = %s
        story_text = %s
        story_author = %s
        """ % (story_id,story_date,category_id,story_title,story_summary,story_text,story_author)

        move_on = raw_input("Does this look right? (y/n) ")
        move_on = convertRaw(move_on)


    print "Beginning to read in the stories database."

    print " "
    print " "
    print "             BEGINNING TO READ IN STORIES               "
    print " ############################################################ "
    print " ############################################################ "
    print " ############################################################ "
    print " ############################################################ "
    print " ############################################################ "
    print " "
    print " "

    storiesCSV = csv.reader(open('stories.csv'), delimiter=',', quotechar='"')
    stories = []
    i = 0
    for line in storiesCSV:
        if i == 0:
          print " ############################################################ "
          print " ############################################################ "
          print "                           CUSTOM SITE                        "
          print " ############################################################ "
          print " ############################################################ "
          print " "
          print "  SHOWING STORY STRUCTURE  "
          print " "
          print " "
          print " "
          print " "
          i += 1
        else:
          x = 0
          for bit in line:
             print str(x)+"    "+bit
             x = x + 1
             if x > 12:
                print "FAILURE"
                x = 1/0
          print " "
          print " "

          story = [
            line[int(story_id)],
            line[int(story_date)],
            line[int(section_id)]+","+line[int(category_id)] if (section_id and trans_filename) else line[int(category_id)],
            line[int(story_title)],
            line[int(story_summary)],
            line[int(story_text)],
            line[int(story_author)],
        ]


          stories.append(story)
          i += 1
    print "All "+str(i)+" stories read in."

    print " "
    print " "
    print "                BEGINNING TO ADD NEW CONTENT"
    print " ############################################################ "
    print " ############################################################ "
    print " ############################################################ "
    print " ############################################################ "
    print " ############################################################ "

    for story in stories:
        user = story[6]
        category = story[2]

        post_id = len(PostList) + 1
        id_num = story[0]
        post_date = story[1]
        post_title = story[3]
        post_excerpt = story[4]
        post_content = story[5]
        post_subheadline = story[7]

        print "Adding a new post."
        print "     from story " + str(story[0])
        print "     idNumber:  " + str(post_id)
        print "     Title:     " + post_title[:50]



        if trans_filename:
            cat_ids = category.split(",")
            try:
                c = Category(trans[headerl[0]][cat_ids[0]])
                CategoryList = addCat(CategoryList,c.get_name())
            except KeyError:
                print "No Section"
            try:
                cc = Category(trans[headerl[1]][cat_ids[1]])
                CategoryList = addCat(CategoryList,cc.get_name())
            except KeyError:
                print "No Category"
            categories = [c,cc]
        else:
            categories = [Category(category)]
        newPost = Post(post_id,categories,user,post_date,post_content,post_title,post_excerpt,id_num)
        PostList.append(newPost)
    print str(len(PostList))+" posts added."
    return CategoryList,PostList

def addCat(CategoryList,category):
    #horribly inefficient
    unique_category = True
    for existing_category in CategoryList:
        if category == existing_category.get_name():
            unique_category = False

    if unique_category:
        print "Adding a new category."
        print "     category name: " + category
        newCategory = Category(category)
        CategoryList.append(newCategory)
    return CategoryList

def createStructures(CategoryList,PostList,stories,settings):
    if settings['verbose_results']:
        print " "
        print " "
        print "                BEGINNING TO ADD NEW CONTENT"
        print " ############################################################ "
        print " ############################################################ "
        print " ############################################################ "
        print " ############################################################ "
        print " ############################################################ "
    for story in stories:
        user = story[6]
        category = story[2]

        post_id = len(PostList) + 1
        identification_num = story[0]
        post_date = story[1]
        post_title = story[3]
        post_excerpt = story[4]
        post_content = story[5]
        subheadline = story[7]
        
        categories = category.split(':')
        all_categories = []

        # For each category that isn't empty, check whether it's unique and append it to the Post object
        for category in categories:
          if category != '':
            unique_category = True
            for existing_category in CategoryList:
              if category == existing_category.get_name():
                  unique_category = False
                
            newCategory = Category(category)
            all_categories.append(newCategory)
          
            if unique_category:
              if settings['verbose_results']:
                  print "Adding a new category."
                  print "     category name: " + category
              CategoryList.append(newCategory)
                    
        newPost = Post(post_id,all_categories,user,post_date,post_content,post_title,post_excerpt,identification_num)

        #if (newPost.pubDate >= import_start_date):
        #    if settings['verbose_results']:
        #        print "Adding a new post."
        #        print "     from story " + str(story[0])
        #        print "     idNumber:  " + str(post_id)
        #        print "     Title:     " + post_title[:50]
        PostList.append(newPost)

    print str(len(PostList))+" posts added."
    return CategoryList,PostList

def addImages(PostList,images,settings):
    if settings['verbose_results']:
        print " "
        print " "
        print "                BEGINNING TO ADD NEW IMAGES"
        print " ############################################################ "
        print " ############################################################ "
        print " ############################################################ "
        print " ############################################################ "
        print " ############################################################ "

    # Read CP4 images from media.csv
    if len(images) == 0:
        mediaCSV = csv.reader(open('media.csv'), delimiter=',', quotechar='"')
        media = []
        for line in mediaCSV:
            item = [line[0],line[1],line[2],line[3]]
            media.append(item)

        completeList = []
        i       = 0
        skipped = 0
        added   = 0
        for image in media:
            i += 1
            firstImg = True
            identification_num = image[0]
            for idNum in completeList:
                if idNum == identification_num:
                    firstImg = False
            if firstImg:
                added += 1
                completeList.append(identification_num)
                for Post in PostList:
                    if Post.checkID(identification_num):
                        if settings['verbose_results'] and firstImg:
                            print "Adding image to a post."
                            print "     Image # " + str(i)
                            print "     Post ID " + str(identification_num)
                        filename = image[1]
                        caption = image[2]
                        credit = image[3]
                        Post.addImage(filename,credit,settings)
            else:
                skipped += 1
        print "Done with images."
        print "          total: "+str(i)
        print "       inserted: "+str(added)
        return PostList
    else:
        i = 0
        for image in images:
            i += 1
            identification_num = image[0]
            filename   = image[1]
            credit     = image[2]
            for Post in PostList:
                try:
                    if Post.checkID(identification_num):
                        if settings['verbose_results']:
                            print "Adding image to a post."
                            print "     File    " + filename
                            print "     Image # " + str(i)
                            print "     Post ID " + str(identification_num)
                        caption = None
                        credit = credit.replace("'","\\'")
                        Post.addImage(filename,caption,credit,settings)
                except:
                    pass
        print "Done with images."
        print "          total: "+str(i)
        return PostList


def createFile(name,header,meta,categories):
    xml_file = open(name+".xml",'w')

    xml_file.write(header)
    xml_file.write(meta)
    xml_file.write(categories)

    return xml_file

def writeFiles(SiteInfo,PostList,CategoryList,settings):
    # Now to add the meat ...

    print "Creating the XML Files ..."

    print " 1. Creating the header."
    header = """<?xml version="1.0" encoding="UTF-8"?>
<!-- This is a WordPress eXtended RSS file generated by the CoPress conversion script. -->
<!-- It contains information about your site's posts, and categories. -->
<!-- You may use this file to transfer that content from one site to another. -->

<!-- generator="WordPress/2.7.1" -->
<rss version="2.0"
    xmlns:excerpt="http://wordpress.org/export/1.0/excerpt/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:wfw="http://wellformedweb.org/CommentAPI/"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:wp="http://wordpress.org/export/1.0/"
>

<channel>
    """

    print " 2. Creating site meta-data."
    metadata = SiteInfo

    print " 3. Adding categories."
    i = 0
    category = """ """
    for catObj in CategoryList:
        i = i+1
        category = category + catObj.get_item()

    i = 0
    x = 1

    xml_end = """    </channel>
        </rss>
        
        """

    if not os.path.exists('Output'):
        os.mkdir('Output')

    for postObj in PostList:
        if i == 0:
            print " 3."+str(x)+" Creating new file."
            name = "Output/CoPress Import File - "+str(x)
            xml_file = createFile(name,header,metadata,category)
            x = x + 1
        i = i+1
        xml_file.write(postObj.get_item(settings))
        if i == settings['posts_per_file']: # Splits files to make sure they don't get too big.
            xml_file.write(xml_end)
            i = 0


def importStories(settings):
    print "Beginning to read in the stories database."

    """
    CP 4 Structure
                        CP4 Line    Converter   Description
    "Story_id"          line[0]     story[0]    Sets the story id
    "Priority"          line[1]
    "Issue_Date"        line[2]     story[1]    Sets the post date and time
    "Section_Name"      line[3]     story[2]    Sets the category name
    "Headline"          line[4]     story[3]    Sets the headline
    "SubHeadline"       line[5]     story[7]    Sets the subheadline            
    "Summary"           line[6]     story[4]    Sets the post excerpt
    "Story_Text"        line[7]     story[5]    Sets post content
    "Author"            line[8]     story[6]    Sets a user display name

    CP 5 Structure
                        CP5 Line    Converter   Description
    Content ID          line[0]     story[0]   
    Creation Date       line[1]     story[1]    Sets the post date - no post date
    Title               line[2]     story[3]    
    Subtitle            line[3]     story[7]    Sets the subheadline
    Byline              line[4]     story[6]    Sets a user display name
    Second Byline       line[5]
    Image Content ID    line[6]
    Image Name          line[7]     filename
    Image Title         line[8]     imagename
    Image Caption       line[9]
    Image Copyright     line[10]    credit
    Summary             line[11]    story[4]    Sets the post excerpt
    Text                line[12]    story[5]    Sets the post content    
    
    """

    """
    One error I have encountered is finding NUL bytes. If you see this error, run the below not in verbose mode. 
    Search the text that is produced for "NUL," find that section of the csv file and run a find-and-replace to remove the null characters.
    """
    # print open('stories.csv').read().replace("\0", ">>>NUL<<<")
    # x = 1/0

    if settings['verbose_results']:
        print " "
        print " "
        print "                BEGINNING TO READ IN STORIES                  "
        print " ############################################################ "
        print " ############################################################ "
        print " ############################################################ "
        print " ############################################################ "
        print " ############################################################ "
        print " "
        print " "
        print "                CHECKING DATABASE TYPE                        "
        print " ############################################################ "

    storiesCSV = csv.reader(open('stories.csv'), delimiter=',', quotechar='"')
    stories = []
    images  = []
    i = 0
    for line in storiesCSV:
        if i == 0:
            if line[1] == "Priority":
                version = 4
            else:
                version = 5

                # column ordering can vary by CP5 export, so create a lookup table
                cp5_map = {
                    'images': [],
                    'comments': [],
                }
                for c, column in enumerate(line):
                    if len(column) > 0:
                        if ':' not in column:
                            cp5_map[column] = c
                        else:
                            if 'Comment' in column:
                                cp5_map['comments'].append(c)
                            elif 'Image' in column:
                                cp5_map['images'].append(c)
            if settings['verbose_results']:
                print " ############################################################ "
                print " ############################################################ "
                print "                     CP"+str(version)+"                       "
                print " ############################################################ "
                print " ############################################################ "
                print " "
                print "  SHOWING STORY STRUCTURE  "
                print " "
                print " "
                print " "
                print " "
            i += 1
        else:
            if settings['verbose_results']:
                x = 0
                for bit in line:
                    print str(x)+"     "+bit
                    x = x + 1
                print " "
                print " "
            if version == 4:
                story = [line[0],line[2],line[3],line[4],line[6],line[7],line[8],line[5]]

            if version == 5:
                if settings['verbose_results']: "Cleaning CP5 data"
                content_id = line[0]
                if content_id[0] == "m":
                    content_id = content_id.split(".")
                    content_id = content_id[2]
                else:
                    content_id = content_id.split(".")
                    content_id = content_id[1]
                # story = [content_id,line[1],"CP5 - MISSING",line[2],line[11],line[12],line[4],line[3]] # Normal CP 5
                # story = [content_id,line[1],"CP5 - MISSING",line[2],line[8],line[9],line[4],line[3]] # CP 5 variation we've seen
                # story = [content_id,line[1],line[8],line[2],line[6],line[7],line[4],line[3]] # CP 5 variation we've seen
                #story = [content_id,line[1],line[9],line[2],line[7],line[8],line[4],line[3]] # CP 5 variation 2 we've seen
                story = [
                    content_id,
                    line[cp5_map['Creation Date']],
                    line[cp5_map['Categorization']],
                    line[cp5_map['Title']],
                    line[cp5_map['Summary']],
                    line[cp5_map['Text']],
                    line[cp5_map['Byline']],
                    line[cp5_map['Subtitle']],
                ]

                try:
                    for imagecolumn in cp5_map['images']:
                        imageline = line[imagecolumn].strip()
                        if len(imageline) > 0:
                            try:
                                imageinfo = imageline.split(':')
                                filename = imageinfo[1]
                                credit = imageinfo[4]

                                image = [content_id,filename,credit]
                                images.append(image)
                            except:
                                print 'Error on %d image' % i
                except:
                    imageline = line[cp5_map['images']].strip()
                    if len(imageline) > 0:
                        try:
                           imageinfo = imageline.split(':')
                           filename = imageinfo[1]
                           credit = imageinfo[4]

                           image = [content_id,filename,credit]
                           images.append(image)
                        except:
                           print 'Error on %d image' % i

                # if line[7] != "" and line[8] != "imageexists":
                #     filename = line[7]
                #     if len(line) > 10:
                #         credit = line[10]
                #     else: # in the odd structures we've seen.
                #         credit = ""
                #     image = [content_id,filename,credit]
                #     images.append(image)

            stories.append(story)
            i += 1
    print "All "+str(i)+" stories read in."
    return version,stories,images

def convertRaw(answer):
    if answer == "y" or answer == "yes" or answer == "Y":
        return True
    else:
        return False

def configureSettings():
    config = ConfigParser.RawConfigParser()
    settings = {}
    # (optional) Use a config file
    settings['config_file'] = raw_input("Please enter config filename (optional): ")
    while settings['config_file']:
        try:
            config.readfp(open(settings['config_file']))
            config.read(settings['config_file'])
            break
        except:
            settings['config_file'] = raw_input("Invalid file. Please enter config filename (optional): ")
    
    # Archives format
    settings['archives_format'] = False
    # @todo There's probably an easier way to see if it's a part of a list. Or we could check the format for the user
    while settings['archives_format'] != 'cp4' and settings['archives_format'] != 'cp5' and settings['archives_format'] != 'custom':
        try:
            settings['archives_format'] = config.get('basic', 'archives_format')
            print "Your archive format is: " + settings['archives_format']
        except:
            settings['archives_format'] = raw_input("What format are your archives? 'cp4', 'cp5' or 'custom': ")

    # Website URL
    settings['website_url'] = ''
    # @todo Check if it's a valid URL
    while settings['website_url'] == '':
        try:
            settings['website_url'] = config.get('basic', 'website_url')
            print "Your website URL is: " + settings['website_url']
        except:
            settings['website_url'] = raw_input("What is your new website's URL: ")
    
    # Verbose results
    try:
        settings['verbose_results'] = config.getboolean('basic', 'verbose_results')
        print "Show verbose results: " + settings['verbose_results']        
    except:
        settings['verbose_results'] = raw_input("Do you want verbose results? (Y/n): ")
        settings['verbose_results'] = convertRaw(settings['verbose_results'])
    
    
    # Author settings
    settings['author_association'] = False
    while settings['author_association'] == False:
        try:
            settings['author_association'] = config.get('basic', 'author_association')
            print "Authors will be associated with posts as: " + settings['author_association']
        except:
            settings['author_association'] = raw_input("How should authors be associated with posts? ('custom field' or 'user'): ")
            if settings['author_association'] != 'custom field' and settings['author_association'] != 'user':
                settings['author_association'] = False
    
    # (optional) Which custom field to store the images in
    settings['author_custom_field'] = ''
    if settings['author_association'] == 'custom field':
        while settings['author_custom_field'] == '':
            try:
                settings['author_custom_field'] = config.get('basic', 'author_custom_field')
                print "Authors will be stored in this custom field: " + settings['author_custom_field']
            except:
                settings['author_custom_field'] = raw_input("Which custom field should authors be stored in?: ")
    
    # Image settings
    settings['image_association'] = False
    while settings['image_association'] == False:
        try:
            settings['image_association'] = config.get('basic', 'image_association')
            print "Images will be associated with posts as: " + settings['image_association']
        except:
            settings['image_association'] = raw_input("How should images be associated with posts? ('custom field' or 'insert'): ")
            if settings['image_association'] != 'custom field' and settings['image_association'] != 'insert':
                settings['image_association'] = False
    
    # (optional) Which custom field to store the images in
    settings['image_custom_field'] = ''
    if settings['image_association'] == 'custom field':
        while settings['image_custom_field'] == '':
            try:
                settings['image_custom_field'] = config.get('basic', 'image_custom_field')
                print "Images will be stored in this custom field: " + settings['image_custom_field']
            except:
                settings['image_custom_field'] = raw_input("Which custom field should images be stored in?: ")
    
    # (optional) Import start date
    settings['import_start_date'] = False
    while settings['import_start_date'] == False:
        try:
            settings['import_start_date'] = config.get('basic', 'import_start_date')
            print "Posts will be added from this day forward: " + settings['author_custom_field']
        except:
            settings['import_start_date'] = raw_input("Would you like to specify a start date for your import? (optional, YYYY-MM-DD): ")
            try:
                settings['import_start_date'] = datetime.datetime.strptime(start_date,"%Y-%m-%d")
            except:
                settings['import_start_date'] == ''
                
    # Prepend image file path (deals with file size)
    try:
        settings['prepend_image_file_path'] = config.get('basic', 'prepend_image_file_path')
        print "File path to be prepended to images: " + settings['prepend_image_file_path']        
    except:
        settings['prepend_image_file_path'] = '/wp-content/uploads'
        print "File path to be prepended to images: " + settings['prepend_image_file_path'] 
                
    # Posts per file (deals with file size)
    try:
        settings['posts_per_file'] = config.getint('basic', 'posts_per_file')
        print "Posts per file: " + settings['posts_per_file']        
    except:
        settings['posts_per_file'] = 300
         print "Posts per file: " + settings['posts_per_file']
            
    return settings

def main():
    print "Welcome to the College Publisher database converter, from CoPress Inc. ( http://copress.org )"
    settings = configureSettings()
    
    if settings['archives_format'] != 'cp4' and settings['archives_format'] != 'cp5':
        CategoryList,PostList = custom(want_custom)
    else:
        PostList = []
        CategoryList = []
        print "This script will create a WordPress eXtended RSS file."
        print "You can merge it with your existing site easily."

        version,stories,images = importStories(settings)

        CategoryList,PostList = createStructures(CategoryList,PostList,stories,settings)
        
        # Add the images to all of the posts
        PostList = addImages(PostList,images,settings)

    SiteInfo = """
<title>CoPress Import</title>
<link>%s</link>
<pubDate>%s</pubDate>
<generator>CoPress Convert (v 1.1a)</generator>
<language>en</language>
<wp:wxr_version>1.0</wp:wxr_version>
<wp:base_site_url>%s</wp:base_site_url>
<wp:base_blog_url>%s</wp:base_blog_url>
                """ % (settings['website_url'],time.strftime("%Y-%m-%d %I:%M%p",time.localtime()),settings['website_url'],settings['website_url'])

    writeFiles(SiteInfo,PostList,CategoryList,settings)

    print ""
    print ""
    print "Done!"
    print ""
    print ""


if __name__ == '__main__':
    main()
