import curses
import sqlite3
import sys

class Log:
    def __init__(self):
        self.logs = []

    def log(self, message):
        self.logs.append(message)

    def dump(self):
        return "\n".join(self.logs)

def drawList(screen, items, line, character, assembleString= lambda datum : str(datum[0]), num=5):
    for(i,item) in enumerate(items):
        if i <= num:
            screen.addstr(line + i, character, assembleString(item))
    screen.refresh()

class Field:
    def __init__(self, name, line, character, screen, data={}, assembleString = lambda datum: str(datum[0])):
        self.name = name
        self.search = ""
        self.line = line
        self.character = character
        self.screen = screen
        self.data = data
        self.filteredData = data
        self.choice = None;
        self.assembleString = assembleString
        screen.addstr(line,character,name+": ")
        drawList(screen,self.filteredData,line+2,character,self.assembleString)

    def cursorToStart(self):
        screen.move(self.line+1,self.character+len(self.search))

    def handleChar(self, c):
        raise Exception("handleChar not implemented")

    def select(self):
        raise Exception("select not implemented")

    def getChoice(self):
        return self.choice

class NumberField(Field):
    def handleChar(self,c):
        self.cursorToStart()
        if c == 127: #backspace
            self.search = self.search[0:len(self.search)-1]
            screen.move(self.line+1,self.character)
            screen.addstr(self.search+" ")
            screen.move(self.line+1,self.character+len(self.search))
        elif c in range(48,58):
            self.search += chr(c)
            screen.move(self.line+1,self.character)
            screen.addstr(self.search)
            screen.move(self.line+1,self.character+len(self.search))

    def select(self):
        if(len(self.search) > 0):
            self.choice = float(self.search)

class SearchField(Field):
    def handleChar(self, c):
        self.cursorToStart()
        self.search += chr(c)
        if c == ord('D'):
            screen.move(self.line+1,self.character)
            screen.addstr(" "*len(self.search))
            screen.move(self.line+1,self.character)
            self.search = ""
        elif c == 127: #backspace
            self.search = self.search[0:len(self.search)-2]
            screen.move(self.line+1,self.character)
            screen.addstr(self.search+" ")
            screen.move(self.line+1,self.character+len(self.search))
        erase = [[".........................................."] for self.datum in self.filteredData]
        self.filteredData = [datum for datum in self.data if self.search.upper() in self.assembleString(datum).upper()]
        drawList(self.screen,erase,self.line+2,self.character)
        drawList(self.screen, self.filteredData, self.line+2, self.character, self.assembleString)
        screen.move(self.line+1,self.character)
        screen.addstr(self.search)
        screen.refresh()

    def select(self):
        erase = [[".........................................."] for i in range(len(self.data))]
        drawList(self.screen,erase,self.line+2,self.character)
        screen.move(self.line+1,self.character)
        if len(self.filteredData) > 0 and len(self.search) > 0:
            self.search = self.assembleString(self.filteredData[0])
            screen.addstr(self.search)
            self.choice = self.data.index(self.filteredData[0])

class Error:
    def __init__(self, line, character, screen, types):
        self.type = None;
        self.pointsLost = None;
        self.line = line;
        self.character = character;
        self.screen = screen;
        self.types = types;

    def deploy(self):
        self.type = SearchField("Type", self.line, self.character, self.screen, self.types, lambda type: f"{type[0]} {type[1]}")
        self.pointsLost = NumberField("Points Lost", self.line, self.character + 35, self.screen)
        return self.type, self.pointsLost

    def getChoices(self):
        if self.type == None or self.pointsLost == None:
            raise Exception("Error not deployed")
        return [self.type.choice, self.pointsLost.choice]

class NewTypeField:
    def __init__(self, line, character, screen, cursor):
        self.line = line;
        self.character = character;
        self.screen = screen;
        self.value = "";
        self.cursor = cursor;
        screen.move(self.line,self.character)
        screen.addstr("Create New Type: ")

    def cursorToStart(self):
        self.screen.move(self.line+1,self.character)

    def handleChar(self,c):
        self.cursorToStart()
        if c == 127: #backspace
            self.value = self.value[0:len(self.value)-1]
            screen.move(self.line+1,self.character)
            screen.addstr(self.value+" ")
            screen.move(self.line+1,self.character+len(self.value))
        elif c == 10: #enter
            self.createNewType()
        else:
            self.value += chr(c)
            screen.move(self.line+1,self.character)
            screen.addstr(self.value)
            screen.move(self.line+1,self.character+len(self.value))

    def select(self):
        pass

    def createNewType(self):
        self.cursor.execute("INSERT INTO types (description) VALUES (?)", (self.value,))



class FocusManager:
    def __init__(self, data, width, height):
        self.data = data
        self.currentX = 0
        self.currentY = 0
        self.width = width
        self.height = height

    def setFocus(self, indexX, indexY):
        if self.data[indexY][indexX] != None:
            self.currentX = indexX
            self.currentY = indexY
            self.data[self.currentY][self.currentX].cursorToStart()

    def selectCurrent(self):
        self.data[self.currentY][self.currentX].select()

    def handleChar(self, c):
        if c in [ord('L'), ord('H'), ord('J'), ord('K')]:
            if c == ord('H') and self.currentX > 0:
                self.data[self.currentY][self.currentX].select()
                self.setFocus(self.currentX-1, self.currentY)
            elif c == ord('J') and self.currentY < self.height-1:
                self.data[self.currentY][self.currentX].select()
                self.setFocus(self.currentX, self.currentY+1)
            elif c == ord('K') and self.currentY > 0:
                self.data[self.currentY][self.currentX].select()
                self.setFocus(self.currentX, self.currentY-1)
            elif c == ord('L') and self.currentX < self.width-1:
                self.data[self.currentY][self.currentX].select()
                self.setFocus(self.currentX+1, self.currentY)

        elif self.currentX < self.width and self.currentY < self.height and self.data[self.currentY][self.currentX] != None:
            self.data[self.currentY][self.currentX].handleChar(c)

class DataEntry:
    def __init__(self, connection, classid, homeworkid, nonErrors, problems):
        self.connection = connection
        self.classid = classid
        self.homeworkid = homeworkid
        self.nonErrors = nonErrors if nonErrors != None else 0
        self.problems = problems

    def log(self,log):
        log.log("class: "+str(self.classid) + " homework: "+str(self.homeworkid) + " nonError count: " + str(int(self.nonErrors)) + " problems: "+str(self.problems))

    def confirm(self):
        print("class:",self.classid)
        print("homework:",self.homeworkid)
        print("you got", self.nonErrors, "right out of", int(self.nonErrors) + len(self.problems))
        print("problems:")
        for problem in self.problems:
            print(problem)
        print("is this correct? (y/n)")
        return input() in ["y","Y"]

    def execute(self):
        for problem in self.problems:
            self.connection.execute("INSERT INTO problems (classid, homeworkid, typeid, lost) VALUES (?, ?, ?, ?)", (self.classid, self.homeworkid, problem[0][0], problem[1]))
        for _ in range(int(self.nonErrors)):
            self.connection.execute("INSERT INTO problems (classid, homeworkid, typeid, lost) VALUES (?, ?, ?, ?)", (self.classid, self.homeworkid, 0, None))

def loadData(cursor):
    classes = cursor.execute("SELECT classid,class,code,name,classes.professorid FROM classes INNER JOIN professors ON classes.professorid==professors.professorid")
    classes = classes.fetchall()
    types = cursor.execute("SELECT typeid,description FROM types")
    types = types.fetchall()
    return classes, types

def main(screen):
    width = 4
    height = 5
    data = []
    errors = []

    for row in range(height):
        row = []
        for col in range(width):
            row.append(None)
        data.append(row)

    
    if len(sys.argv) != 2:
        raise Exception("Usage: python3 homework.py <database>")
    else:
        database = sys.argv[1]

    cnx = sqlite3.connect(database)
    cursor = cnx.cursor()
    classes, types = loadData(cursor)

    for row in range(1,height):
        for col in range(int(width/2)):
            errors.append(Error((row*9), col*50, screen, types))

    def assembleClassString(datum):
        return f"{datum[0]} {datum[1]} {datum[2]} {datum[3]} (professor {datum[4]})"

    data[0][0] = SearchField("Class", 0, 0, screen, classes, assembleString=assembleClassString) # class field
    data[0][1] = NewTypeField(0, 50, screen, cursor) # field to create new types
    data[0][2] = NumberField("Non-Errors", 0, 80, screen) # number of non-errors
    for i in range(1,height):
        data[i][0], data[i][1] = errors[2*i-2].deploy()
        data[i][2], data[i][3] = errors[2*i-1].deploy()

    data[0][0].cursorToStart()
    manager = FocusManager(data, width, height)

    while True:
        c = screen.getch()
        if c == ord('Q'):
            manager.selectCurrent()
            break
        elif c == ord('R'):
            classes, types = loadData(cursor)
            for error in errors:
                if error.type != None:
                    error.type.data = types
        else:
            manager.handleChar(c)

    log.log("getting choices")

    Class = data[0][0].getChoice()
    if Class != None:
        Class = classes[Class][0]

    maxHomeworkId = cnx.execute("SELECT MAX(homeworkid) FROM problems").fetchone()[0]
    newHomeworkId = maxHomeworkId + 1 if maxHomeworkId != None else 0

    nonErrors = data[0][2].getChoice()
    if nonErrors == None: nonErrors = 0

    choices = []

    for error in errors:
        cs = error.getChoices()
        if cs[0] != None and cs[1] != None:
            choices.append([types[cs[0]], cs[1]])


    log.log("creating dataentry")
    dataentry = DataEntry(cnx, Class, newHomeworkId, nonErrors, choices)
    # dataentry.log(log)
    dataentry.execute()
    curses.endwin()
    confirmed = dataentry.confirm()
    if confirmed:
        cnx.commit()
    cnx.close()


log = Log()

try:
    screen = curses.initscr()
    curses.noecho()
    main(screen)
    curses.endwin()
except Exception as e:
    curses.endwin()
    print(e)
finally:
    curses.echo()
    print(log.dump())
