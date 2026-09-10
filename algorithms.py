import gemmi
from gemmi import cif # type: ignore
import math
import random
import os #for removing uploaded file from folder after copying
import numpy as np #numpy for arrays and maths

# ____________________________________________________________
# __________________ READING CIF CLASS __________________
# ____________________________________________________________


class cifReaderClass:
    # attributes 
    document = ""
    block = ""
    errorMessage = ""
    inputUnitCell = []
    inputFracCoordMatrix = np.array([["?"],["?"],["?"]])
    inputCoordTable = [[]] #2D array
    inputCoordTableTags = []
    inputNumOfAtoms = 0
    validCif=False
        
    def readInputCIF(self,path):
        """Method that runs the rest of the methods required to read the necessary info from the CIF one at a time.
        Parameters: 
            path (string): The path of the file to be read.
        Returns: 
            boolean or string: 'True' if CIF was read successfully, a string error message if not 
        """
        # Subsection for file path
        if self.validatePath(path) == False:
            rtn = self.errorMessage
        # Subsection for picking which block in CIF to read
        elif self.findBlockNumber() == -1:
            rtn=(self.errorMessage)
        # Subsection for extracting and validating  unit cell information
        elif self.findUnitCellList()==False:
            rtn=(self.errorMessage)
        # Subsection for extracting and validating fractional coordinates of all the atoms
        elif self.findFracCoordinates()==False:
            rtn=(self.errorMessage)
        else:
            self.validCif = True
            print("")
            print("CIF read successfully.")
            rtn= True
        if path!="example_T2Crystal.cif" and path!="example_NaCl.cif":
            os.remove(path)
        print("file name: ",path)
        return rtn

    def setDocumentBlock(self, blockNumber):
        """Method that carefully tries to access the whole block, and prints an error if the block doesn't exist
        Parameters: 
            blockNumber (integer): The path of the file to be read.
        """
        try: # Try except in case of trying to override with a block that doesn't exist
            self.block = self.document[blockNumber]
        except IndexError:
            print("Block", blockNumber, " does not exist in CIF.") # Error message
            self.errorMessage=self.errorMessage+"Block", blockNumber, " does not exist in CIF."
            
    def findBlockNumber(self):
        """Method that finds the first block that contains structure information
        Returns: 
            integer: The block number that contains _cell_length_a so is likely to contains all necessary information.
        """
        blockNumber = -1 # findBlockNumber returns -1 if whole file does not contain any cell_length_a info
        self.errorMessage = "The CIF does not contain any _cell_length_a information"
        for i in range(0,len(self.document)): # loops through all data blocks
            block = self.document[i]
            if block.find_pair('_cell_length_a')!=None:
                blockNumber=i
                self.setDocumentBlock(blockNumber)
                break
        return blockNumber

    def sanitiseDataEntry(self, data):
        """Method that sanitises input then and validates whether it can be converted to a float.
        Parameters: 
            data (string): The data that is hopefully numeric but is currently string
        Returns: 
            string: '?' if the string cannot be successfully converted to a float, or the sanitised float as a string 
        """
        if data==None:
            return(False)
        # Firstly converts input string to a list of characters, then checks whether each character is a number/bracket/other
        cellDataList=[] # Defining list 'cellDataList' that will store the list version of the input string        
        for char in data: # For loop that places the string parameter into a list'cellDataList'
            cellDataList.append(char)
        # Loop below picks suitable characters for output
        rtnData="" # String copied into a list so can begin building a string that is a valid float
        decimalPlacePresent = False # Variable keeps track of number of fullstops so that only 1 decimal point is accepted
        for i in range(len(cellDataList)):
            if cellDataList[i].isnumeric() == True:
                rtnData=rtnData+cellDataList[i] # Code adds variable to the final string
            elif cellDataList[i]=='.' and decimalPlacePresent == False: #If there is no decimal point previously, fine to add it
                decimalPlacePresent = True
                rtnData=rtnData+'.'
            elif cellDataList[i] == "(":
                for j in range (i,len(cellDataList)): # For loop that iteratively removes every element at [i] until all characters after and including "(" are removed
                    cellDataList.pop(i)
                break # Once there is a bracket, all next characters are deleted so must break out of for loop to avoid invalid index errors.     
            elif i==0 and cellDataList[i]=="-": #if there is a negative symbol at the start, leave it be
                rtnData="-"
            else:
                self.errorMessage = '"'+ data + '"' + " is not a suitable float."
                rtnData="?"
                break
        return(rtnData)

    def validatePath(self, path):
        """Method that tries to open the file and catches errors if they arise
        Parameters: 
            path (string): The path of the file to be read.
        Returns: 
            boolean: True if the path can be read successfully, False if not 
        """
        rtn = True
        try: 
            self.document = cif.read_file(path)
        except FileNotFoundError:
            self.errorMessage = "CIF file not in folder. Check the path." # Error message
            rtn = False
        except RuntimeError as err:
            self.errorMessage = "Check the CIF. Error details:" + str(err) # Error message
            rtn = False
        except:
            self.errorMessage = "Check that input file is a correctly formatted CIF"
            rtn = False
        return(rtn)

    def findUnitCellList(self):
        """Method that put the unit cell parameters in the CIF to the class attribute inputUnitCell 
        Returns: 
            boolean: True if the unit cell parameters can be read successfully, False if not 
        """
        # unitCellItems is a 2d list that stores the names of the data that relates to the unit cell and the data items themselves will be added to the 2nd row of the list
        unitCellItems = [['_cell_length_a', '_cell_length_b', '_cell_length_c', '_cell_angle_alpha', '_cell_angle_beta', '_cell_angle_gamma'],["","","","","",""]]
        countValid = 0 # Temporary variable that counts how many unit cell values are correctly formatted. There must be 6 for the program to continue.
        # For loop that goes through unitCellItems list, in order to collect the 6 unit cell data items from the CIF
        for i in range(0,6):
            # If statement that checks whether the data can be converted to a float without errors or not
            readUnitCellData = self.sanitiseDataEntry(self.block.find_value(unitCellItems[0][i])) # A 2 element list [0] contains True/False for whether the data can be converted to a string [1] contains the new string
            if readUnitCellData=="?":
                self.errorMessage = "Unit Cell parameter " + str(unitCellItems[0][i]) + " is incorrectly formatted in CIF." + self.errorMessage
                return False
            else:
                unitCellItems[1][i]=float(readUnitCellData) # Can finally safely convert the string into a float without errors.
                countValid =countValid + 1
        # Short if statement that decides whether all unit cell information is present
        if countValid != 6:
            return False
        self.inputUnitCell= unitCellItems[1]
        return(True)

    def findFracCoordinates(self):
        """Method that put the CIF atom fractional coordinates in a matrix of floats (class attribute inputFracCoordMatrix) and all atom info into a 2D list (class attribute inputCoordTables)
        Returns: 
            boolean: True if the fractional coordinates can be read successfully, False if not 
        """
        loop = self.block.find_loop_item('_atom_site_fract_x').loop
        self.inputNumOfAtoms = len(self.block.find_loop('_atom_site_fract_x')) # How many atoms there are.

        fracCoordTags = loop.tags #find the tags of the other data associated with each atom e.g. _atom_site_type_symbol
        if "_atom_site_type_symbol" not in fracCoordTags or "_atom_site_label" not in fracCoordTags: #quick if statement to check that all the necessary columns are present
            self.errorMessage = "The chemical elements or labels of the atoms are not present. "
            return False

        #Finding the coordinates themselves and storing them as a matrix of floats
        fracCoordMatrix = np.array([list(self.block.find_loop('_atom_site_fract_x')),list(self.block.find_loop('_atom_site_fract_y')),list(self.block.find_loop('_atom_site_fract_z'))])
        try:
            fracCoordMatrix= np.vstack(fracCoordMatrix[:, :]).astype(np.float64)
        except ValueError:
            vectorized_sanitiseDataEntry = np.vectorize(self.sanitiseDataEntry) # Vectorize the sanitiseDataEntry function which sanitises the data
            fracCoordMatrix = vectorized_sanitiseDataEntry(fracCoordMatrix)
            try: #Once the data entry has been sanitised, try casting to a float again
                fracCoordMatrix= np.vstack(fracCoordMatrix[:, :]).astype(np.float64)
            except ValueError:
                self.errorMessage = "The coordinates in the file are not suitable floats." + self.errorMessage
                return False
        if np.size(fracCoordMatrix)==0:
            self.errorMessage = "No valid coordinates found"
            return False

        #Code to pull metadata on each coordinate
        coordTable = []
        coordTableTags= ['_atom_site_label','_atom_site_type_symbol','_atom_site_fract_x','_atom_site_fract_y','_atom_site_fract_z']
        coordTable.append(list(self.block.find_loop('_atom_site_label'))) #Adding the label and symbol to the begining of the metadata
        coordTable.append(list(self.block.find_loop('_atom_site_type_symbol')))
        coordTable.append(list(self.block.find_loop('_atom_site_fract_x')))
        coordTable.append(list(self.block.find_loop('_atom_site_fract_y')))
        coordTable.append(list(self.block.find_loop('_atom_site_fract_z')))
        for i in range(0,len(fracCoordTags)): # For loop that adds coordinate metadata to the array
            if i!= fracCoordTags.index('_atom_site_label') and i!=fracCoordTags.index('_atom_site_type_symbol'):
                if fracCoordTags[i]!= '_atom_site_fract_x' and fracCoordTags[i]!= '_atom_site_fract_y' and fracCoordTags[i]!= '_atom_site_fract_z': # Will only add meta data
                    coordTableTags.append(fracCoordTags[i])
                    coordTable.append(list(self.block.find_loop(fracCoordTags[i])))
        self.inputCoordTable = coordTable
        self.inputCoordTableTags = tuple(coordTableTags)
        self.inputFracCoordMatrix=fracCoordMatrix
        return True
    
    
# ____________________________________________________________
# __________________ DISGUISE CRYSTAL CLASS __________________
# ____________________________________________________________

class disguiseCrystalClass:
    
    def orthogonalise(self, unitCellItems): # unitCell parameter is a gemmi unit cell class
        """Method that puts converts unit cell information from CIF into the basis which defines the unit cell.
        Parameters: 
            unitCellItems (gemmi unit cell class): How the library Gemmi stores information about the unit cell.
        Returns: 
            numpy array: storing the basis which defines the unit cell. First column is the first basis vector.
        """
        cell = gemmi.UnitCell(unitCellItems[0],unitCellItems[1],unitCellItems[2],unitCellItems[3],unitCellItems[4],unitCellItems[5])
        originalBasis=cell.orth.mat.tolist()
        originalBasis = np.array(originalBasis)
        return(originalBasis)
    
    def genRandomMatrix(self,upperB):
        """Method that generates a random matrix with determinant 1 (to keep the volume of the unit cell constant).
        Parameters: 
            upperB (integer): The maximum magnitude of the generated integer in each matrix.
        Returns: 
            numpy array: the randomly generated matrix
        """
        lowerB = -upperB #stands for lowerBound
        validMatrix=False # Will be checking that integers in the matrix are less than 20 so that popular programs are able to process the file
        while validMatrix==False:
            validMatrix = True
            #generating 1st matrix
            matrix1 = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
            matrix1[0][1]=random.randint(lowerB, upperB)
            matrix1[0][2]=random.randint(lowerB, upperB)
            matrix1[1][2]=random.randint(lowerB, upperB)
            #generating 2nd matrix
            matrix2 = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
            matrix2[1][0]=random.randint(lowerB, upperB)
            matrix2[2][0]=random.randint(lowerB, upperB)
            matrix2[2][1]=random.randint(lowerB, upperB)
            #combining 2 matricies. 2 matricies required so that z coordinate doesn't stay the same all the time
            matrix=np.dot(matrix1,matrix2)
            for i in range(3):
                for j in range(3):
                    if matrix[i][j]>=20 or matrix[i][j]<=-20:
                        validMatrix = False
        return matrix    

    def convertBasisToUnitCell(self,basis):
        """Method that puts converts the basis that defines the unit cell into unit cell lengths and angles
        Parameters: 
            basis (numpy array): A 3 by 3 matrix with each basis vector in each column.
        Returns: 
            python list: 3 lengths and 3 angles describing the unit cell
        """
        unitCellList = ["","","","","",""]
        v1=np.dot(basis,[1,0,0])
        v2=np.dot(basis,[0,1,0])
        v3=np.dot(basis,[0,0,1])
        unitCellList[0] = np.linalg.norm(v1)*1
        unitCellList[1] = np.linalg.norm(v2)*1
        unitCellList[2] = np.linalg.norm(v3)*1
        unitCellList[3] = math.degrees(math.acos((np.dot(v2,v3))/(np.linalg.norm(v2)*np.linalg.norm(v3))))
        unitCellList[4] = math.degrees(math.acos((np.dot(v1,v3))/(np.linalg.norm(v1)*np.linalg.norm(v3))))
        unitCellList[5] = math.degrees(math.acos((np.dot(v1,v2))/(np.linalg.norm(v1)*np.linalg.norm(v2))))
        return unitCellList

    def fracToEuclideanCoordMatrix(self, basis, fracCoordMatrix):
        return np.dot(basis, fracCoordMatrix)

    def euclideanToFracCoordMatrix(self, basis, euclideanCoordMatrix):
        return np.dot(np.linalg.inv(basis), euclideanCoordMatrix)

    def newBasisFracCoords(self, fracCoordMatrix, transformationMatrix):
        return np.dot(np.linalg.inv(transformationMatrix), fracCoordMatrix)

    def pickExtension(self,upperB):
        """Method that picks 3 random scale factors that will be used to extend each unit cell length.
        Parameters: 
            upperB (integer): The maximum number of times by which wach side can be extended.
        Returns: 
            python list: 3 integers corresponding to the 3 scale factors that will be used to extend each unit cell length
        """
        validExtension=False
        lowerB = 1 #Setting upper and lower bound on the random extensions generated
        while validExtension==False:
            length1sf =random.randint(lowerB,upperB)
            length2sf=random.randint(lowerB,upperB)
            length3sf=random.randint(lowerB,upperB)
            if (length1sf==1) and (length2sf==1) and (length3sf==1):
                validExtension=False
            else:
                validExtension=True
        return [length1sf,length2sf,length3sf]
    
    def extendUnitCell(self,unitCellList,extension):
        """Method that applies to extension to the unit cell parameters
        Parameters: 
            unitCellList (python list): Contains 6 elements, the 3 lengths and 3 angles
            extension (python list): Contains 3 elements that correspond to the 3 scale factors that will be used for extension 
        Returns: 
            python list: Contains 6 elements, the 3 updated lengths and 3 unchanged angles
        """
        for i in range(3):
            if extension[i]!=1:
                unitCellList[i]=extension[i]*unitCellList[i]
        return unitCellList

    def extendFracCoords(self, numOfAtoms, extension, fracCoordMatrix, coordTable,coordTableTags):
        """Method that updates the list of fractional coordinates after extension
        Parameters: 
            numOfAtoms (integer): The number of atoms in the unit cell before extension
            extension (python list): Contains 3 elements that correspond to the 3 scale factors used for extension
            fracCoordMatrix (numpy array): 3 by (numOfAtoms) matrix containing the fractional coordinates
            coordTable (python 2D array): Contains all the info relating to atoms that was found in the CIF 
            coordTableTags (tuple): contains the tag names that provided more info about each atom in the CIF
        Returns: 
            updated numOfAtoms, fracCoordMatrix, coordTable
        """
        rtnFracCoordMatrix = fracCoordMatrix.copy()
        rtnCoordTable = coordTable.copy()
        rtnNumOfAtoms = numOfAtoms
        scalingMatrix = np.eye(3)
        for i in range(3): #Loops through each unit cell length
            scaleFactor = extension[i]
            if scaleFactor!=1:
                setOfCopiedAtoms = [] # a 1D list that will contain the sets of copies as 2D arrays
                for n in range(1,scaleFactor):
                    addingMatrix = np.zeros((3, rtnNumOfAtoms))
                    addingMatrix[i]=n * np.ones(rtnNumOfAtoms)
                    copiedAtoms=rtnFracCoordMatrix + addingMatrix
                    setOfCopiedAtoms.append(copiedAtoms)
                #now concatenate all the sets of copied atoms to the original matrix
                for j in range(scaleFactor-1):
                    rtnFracCoordMatrix = np.concatenate((rtnFracCoordMatrix, setOfCopiedAtoms[j]), axis=1)
                rtnNumOfAtoms = scaleFactor * rtnNumOfAtoms
            scalingMatrix[i][i] = 1/scaleFactor
        rtnFracCoordMatrix = np.dot(scalingMatrix, rtnFracCoordMatrix)
        #now need to update the table, adding rowns and the chemical elements and label
        totalNoOfCopies = extension[0]*extension[1]*extension[2]
        for i in range(len(coordTableTags)):
            rtnCoordTable[i]= totalNoOfCopies * rtnCoordTable[i]
        return rtnNumOfAtoms, rtnFracCoordMatrix, rtnCoordTable

    def applyShifts(self, numOfShifts, maxShift, numOfAtoms, euclideanCoordMatrix):
        """Method that applies a small shifts to some of the atoms
        Parameters: 
            numOfShifts (integer)
            maxShift (float): upper bound of translation in the x,y,z euclidean directions
            numOfAtoms (integer)
            euclideanCoordMatrix (np array): a 3 by NumOfAtoms array containing the Euclidean coordinates of the atoms in the unit cell
        Returns: 
            updated euclideanCoordMatrix
        """
        coordMatrix = euclideanCoordMatrix
        for i in range(numOfShifts):
            position = random.randint(0, numOfAtoms-1)# Picking random position of atom that will be shifted
            translation = np.array([random.uniform(-maxShift, maxShift),random.uniform(-maxShift, maxShift),random.uniform(-maxShift, maxShift)])
            coordMatrix[:,position] = coordMatrix[:,position]+translation
        return coordMatrix

    def applyShiftsToAllAtoms(self,maxShift,numOfAtoms, euclideanCoordMatrix):
        """Method is same as applyShifts but applies the shifts to all of the atoms in the unit cell"""
        coordMatrix = euclideanCoordMatrix.copy()
        shiftMatrix = np.random.rand(3,numOfAtoms) #TIME CONSUMING
        shiftMatrix = maxShift * shiftMatrix
        rtnMatrix=coordMatrix+shiftMatrix
        return rtnMatrix

    def shuffleRows(self,coordTable):
        """Method that shuffles the order of the atoms
        Parameters: 
            coordTable (np array): Contains all the info relating to atoms that was found in the CIF 
        Returns: 
            updated coordTable
        """
        rtnCoordTable = coordTable.copy()
        rtnCoordTable = np.array(rtnCoordTable)
        rtnCoordTable = np.transpose(rtnCoordTable).tolist()
        random.shuffle(rtnCoordTable)
        rtnCoordTable = np.array(rtnCoordTable)
        rtnCoordTable = np.transpose(rtnCoordTable)
        #Note will need to update the labels later
        return rtnCoordTable
    
    


# ____________________________________________________________
# __________________ OUTPUT CLASS ____________________________
# ____________________________________________________________

# Class responsible for creating the output CIF based on an input template CIF
class outputCifClass:
    def __init__(self):
        self.document = "Not set yet"
        self.block = "Set using setTemplate or setTemplateManually"
        self.tolerance = 8

    def setTemplate(self, cifDoc, cifBlock):
        #Method that sets class attributes document and block if you already have them to hand.
        self.document = cifDoc
        self.block =cifBlock

    def setTemplateManually(self, templatePath, blockNumber):
        try:
            self.document = cif.read_file(templatePath)
            self.block = self.document[blockNumber]
        except FileNotFoundError:
            print("CIF file not in folder. Check the path.") # Error message
        except RuntimeError as err:
            print("Check the CIF. Error details:" + str(err)) # Error message
        except IndexError:
            print("Invalid block number")
    
    def updateBlockName(self, newBlockName, newCIFname):
        if newBlockName==None:
            self.block.name="disguised"
        else:
            self.block.name=newBlockName
        self.document.write_file(newCIFname)

    def updateCellAndAtoms(self, unitCellList, numOfAtoms, fracCoordMatrix, coordTable, coordTableTags, newCIFname):
        unitCellDictionary = ['_cell_length_a', '_cell_length_b', '_cell_length_c', '_cell_angle_alpha', '_cell_angle_beta', '_cell_angle_gamma']
        for i in range(0,6):
            self.block.set_pair(unitCellDictionary[i], str(round(unitCellList[i],self.tolerance)))
        # Updating the volume
        newCell = gemmi.UnitCell(unitCellList[0],unitCellList[1],unitCellList[2],unitCellList[3],unitCellList[4],unitCellList[5])
        self.block.set_pair("_cell_volume",str(round(newCell.volume,self.tolerance)))
        # Updating the coordinates: 
        loop = self.block.find_loop_item('_atom_site_fract_x').loop 
        # Moving all coordinates back into the unit cell
        modFracCoordMatrix = fracCoordMatrix.copy() 
        modFracCoordMatrix = np.mod(modFracCoordMatrix, 1)
        for i in range(3): #Updating the x,y,z coordinates in the big table
            coordTable[i+2] = list(map(str,list(map(round, modFracCoordMatrix[i].tolist(),[self.tolerance]*numOfAtoms)))) #Rounding and changing the numbers to strings
        loop.add_columns(coordTableTags[5:], value='NULL')
        loop.set_all_values(coordTable)
        self.document.write_file(newCIFname)

    def updateLabels_AndChemFormulaSum(self,numOfAtoms,coordTable,newCIFname):
        rtnCoordTable = coordTable.copy()
        elementsList = []
        noOfEachElement = []
        for i in range(numOfAtoms):
            element = coordTable[1][i]
            if element not in elementsList:
                elementsList.append(element)
                noOfEachElement.append(1)
            else:
                elementIndex = elementsList.index(element)
                noOfEachElement[elementIndex] = noOfEachElement[elementIndex]+1
            rtnCoordTable[0][i]=element+str(noOfEachElement[elementsList.index(element)]) #updates the label itself
        loop = self.block.find_loop_item('_atom_site_fract_x').loop
        loop.set_all_values(rtnCoordTable)

        #Now setting the formula sum
        chem_formula_sum = "'"
        for j in range(len(elementsList)):
            chem_formula_sum=chem_formula_sum + elementsList[j]+str(noOfEachElement[j])+' '
        chem_formula_sum=chem_formula_sum + "'"
        self.block.set_pair("_chemical_formula_sum",chem_formula_sum)
        self.document.write_file(newCIFname)

    def addMetaData(self,newCIFname,generationInfo):
        '''Method that adds a paragraph to the CIF with information about the disguise transformations applied.
        Ideally, this would be more standardised as the CCDC and collaborators are working on currently. '''
        with open(newCIFname, "a") as file:
            file.write("\n")
            file.write("#"+generationInfo)


# ____________________________________________________________
# __________________ MAIN CLASS ______________________________
# ____________________________________________________________
class main:
    valid = False
    newCifContents = "A valid CIF has not been input"
    randomMatrix=gemmi.Mat33()
    extensionSfs=["1","1","1"]
    numOfShifts=0
    maxShift=0.1
    upperBoundMatrix=5
    shiftAllAtoms = False
    transformBasis = False
    extendBasis = False
    shuffleRows = False
    upperBoundExtension = 3
    shiftAtoms = False
    newCIFname = "newCif.cif"
    newBlockName="disguised"
    generationInfo = "This CIF is based on an input CIF which has been disguised using the following transformations: \n"

    def generateCif(self,inputUnitCellList, inputNumOfAtoms, inputFracCoordMatrix, inputCoordTable,inputCoordTableTags):
        if self.valid==True: #Checks if the input CIF passed the validation checks
            #Python is annoying and wants to do by reference. copy() should ensure that the original isn't being changed
            unitCellList = inputUnitCellList.copy()
            coordTable = inputCoordTable.copy()
            fracCoordMatrix = inputFracCoordMatrix.copy()
            coordTableTags = inputCoordTableTags
            numOfAtoms = inputNumOfAtoms
            
            #Start of actual generateCif stuff
            disguise = disguiseCrystalClass()
            outputCif = outputCifClass()
            outputCif.setTemplateManually("template.cif", 0) # Output CIF will be based on this input template

            if self.transformBasis == True:
                # First, generate the random matrix:
                self.randomMatrix=disguise.genRandomMatrix(self.upperBoundMatrix)

                # First need to convert unit cell and atom coordinates to vectors before performing calculations on them
                basis = disguise.orthogonalise(unitCellList)    
                    
                # Next, transform the basis randomly
                newBasis = np.dot(basis,self.randomMatrix)

                fracCoordMatrix = disguise.newBasisFracCoords(fracCoordMatrix, self.randomMatrix)
                unitCellList = disguise.convertBasisToUnitCell(newBasis)
                self.generationInfo = self.generationInfo + "# The basis (unit cell parameters parameterised) was transformed by applying the following matrix on the right:\n#"+str(self.randomMatrix[0])+"\n#"+str(self.randomMatrix[1])+"\n#"+str(self.randomMatrix[2])+"\n"

            if self.extendBasis == True:
                #First, pick which directions to extend and by how much
                extension = disguise.pickExtension(self.upperBoundExtension) #extension is a 3 element array of scale factors for each unit cell length 
                self.extensionSfs = extension
                unitCellList = disguise.extendUnitCell(unitCellList,extension)
                tempExtendOutputs = disguise.extendFracCoords(numOfAtoms, extension, fracCoordMatrix, coordTable,coordTableTags)
                numOfAtoms = tempExtendOutputs[0]
                fracCoordMatrix= tempExtendOutputs[1]
                coordTable = tempExtendOutputs[2]
                self.generationInfo = self.generationInfo + "# Cell_length_a, cell_length_b, cell_length_c were extended by the corresponding scale factors: " + str(extension) + "\n"

            if self.shiftAtoms==True:
                # Need a list of atoms position vectors in euclidean form.
                # So need to find the vector basis
                basis = disguise.orthogonalise(unitCellList)

                # Convert the fractional coordinates to positon vectors in euclidean.
                euclideanCoordMatrix = disguise.fracToEuclideanCoordMatrix(basis, fracCoordMatrix)
                if self.shiftAllAtoms==True:
                    euclideanCoordMatrix = disguise.applyShiftsToAllAtoms(self.maxShift,numOfAtoms, euclideanCoordMatrix)
                    self.generationInfo = self.generationInfo + "# All atoms were shifted randomly by a maximum of " + str(self.maxShift) + " angstroms.\n"
                else:
                    euclideanCoordMatrix = disguise.applyShifts(self.numOfShifts, self.maxShift, numOfAtoms, euclideanCoordMatrix)
                    self.generationInfo = self.generationInfo + "#" + str(self.numOfShifts) + " atoms were shifted randomly by a maximum of " + str(self.maxShift) + " angstroms.\n"
                fracCoordMatrix = disguise.euclideanToFracCoordMatrix(basis, euclideanCoordMatrix)

            #write to the CIF
            outputCif.updateCellAndAtoms(unitCellList, numOfAtoms, fracCoordMatrix, coordTable, coordTableTags, self.newCIFname) # parameters: a 6 element list containing new unit cell values, the name of the new file

            if self.shuffleRows == True:
                coordTable = disguise.shuffleRows(coordTable)
                self.generationInfo = self.generationInfo + "# The atom order was shuffled. \n"
            outputCif.updateLabels_AndChemFormulaSum(numOfAtoms,coordTable, self.newCIFname) #update the labels and write to the CIF

            outputCif.updateBlockName(self.newBlockName, self.newCIFname)
            outputCif.addMetaData(self.newCIFname,self.generationInfo)
            with open(self.newCIFname, 'r') as file:
                self.newCifContents = file.read()
            