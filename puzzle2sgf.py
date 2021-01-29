#!/usr/bin/python
import requests
import os
import time

downloadWholeCollection =  False
# if False, only the specified puzzle is downloaded
# if True, all problems of the specified puzzle's collection are downloaded

puzzleNumber = 6544
# the puzzle id taken from the puzzle URL

skipAuthentication = True
# authentication is required for private problems

def escape(text):
    return text.replace('\\', '\\\\').replace(']', '\\]')

def writeInitialStones(file, string):
    for i in range(0, len(string), 2):
        file.write('[')
        file.write(string[i:i+2])
        file.write(']')
        
def otherPlayer(player):
    return 'B' if player == 'W' else 'W'
        
def writeCoordinates(file, node):
    file.write(chr(97 + node['x']))
    file.write(chr(97 + node['y']))
    
def writeCoordinatesInBrackets(file, node):
    file.write('[')
    writeCoordinates(file, node)
    file.write(']')
            
def writeMarks(file, marks):
    for mark in marks:
        if 'letter' in mark['marks']:
            file.write('LB[')
            writeCoordinates(file, mark)
            file.write(':')
            file.write(escape(mark['marks']['letter']))
            file.write(']')
        elif 'triangle' in mark['marks']:
            file.write('TR')
            writeCoordinatesInBrackets(file, mark)
        elif 'square' in mark['marks']:
            file.write('SQ')
            writeCoordinatesInBrackets(file, mark)
        elif 'cross' in mark['marks']:
            file.write('MA')
            writeCoordinatesInBrackets(file, mark)
        elif 'circle' in mark['marks']:
            file.write('CR')
            writeCoordinatesInBrackets(file, mark)

def prependText(node, text): 
    if 'text' in node:
        node['text'] = text + '\n\n' + node['text']
    else:
        node['text'] = text
            
def writeNode(file, node, player):
    if 'marks' in node:
        writeMarks(file, node['marks'])
    if 'correct_answer' in node:
        prependText(node, "CORRECT")
    elif 'wrong_answer' in node:
        prependText(node, "WRONG")
    if 'text' in node:
        file.write('C[')
        file.write(escape(node['text']))
        file.write(']')
    if 'branches' in node:
        branches = node['branches']
        for branch in branches:
            if len(branches) > 1:
                file.write('(')
            writeBranch(file, branch, player)
            if len(branches) > 1:
                file.write(')')
        
def writeBranch(file, branch, player):
    file.write(';')
    file.write(player)
    writeCoordinatesInBrackets(file, branch)
    writeNode(file, branch, otherPlayer(player))
        
def writePuzzle(file, puzzle):
    file.write('(;FF[4]CA[UTF-8]AP[puzzle2sgf:0.1]GM[1]GN[')
    file.write(escape(puzzle['name']))
    file.write(']SZ[')
    file.write(str(puzzle['width']))
    if puzzle['width'] != puzzle['height']:
        file.write(':')
        file.write(str(puzzle['height']))
    file.write(']')
    initial_black = puzzle['initial_state']['black']
    if initial_black:
        file.write('AB')
        writeInitialStones(file, initial_black)
    initial_white = puzzle['initial_state']['white']
    if initial_white:
        file.write('AW')
        writeInitialStones(file, initial_white)
    prependText(puzzle['move_tree'], puzzle['puzzle_description'])
    player = puzzle['initial_player'][0].upper()
    file.write('PL[')
    file.write(player)
    file.write(']')
    writeNode(file, puzzle['move_tree'], player)
    file.write(')')
    
def authenticate():
    url = 'https://online-go.com/api/v0/login'
    username =  input('Username: ')
    password =  input('Password: ')
    response = requests.post(url, data={'username' : username, 'password' : password})
    return response.cookies

cookies = [] if skipAuthentication else authenticate()
if downloadWholeCollection:
    collectionUrl = 'https://online-go.com/api/v1/puzzles/'  + str(puzzleNumber) + '/collection_summary'
    collection = requests.get(collectionUrl, cookies=cookies).json()
    time.sleep(5.0)
puzzleUrl = 'https://online-go.com/api/v1/puzzles/' + str(puzzleNumber)
responseJSON = requests.get(puzzleUrl, cookies=cookies).json()
if downloadWholeCollection:
    collectionName = responseJSON['collection']['name']
    collectionFolder = os.getcwd() + '/' + collectionName
    os.mkdir(collectionFolder)
    os.chdir(collectionFolder)
with open(responseJSON['name'] + '.sgf', 'w', encoding="utf-8") as file:
    writePuzzle(file, responseJSON['puzzle'])
if downloadWholeCollection:
    for puzzle in collection:
        if puzzle['id'] != puzzleNumber:
            time.sleep(5.0)
            puzzleUrl = 'https://online-go.com/api/v1/puzzles/' + str(puzzle['id'])
            puzzleJSON = requests.get(puzzleUrl, cookies=cookies).json()['puzzle']
            with open(puzzle['name'] + '.sgf', 'w', encoding="utf-8") as file:
                writePuzzle(file, puzzleJSON)
