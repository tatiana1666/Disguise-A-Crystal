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
    inputElementList = []
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
        elif self.findAllFracCoordinates()==False:
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
            Currently is only used to validate unit cell information, but method is designed to validate and sanitise atom coordinate information
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

    def findAllFracCoordinates(self):
        """Method that finds all the atoms described by the motif, given in any space group, updating the class attributes inputFracCoordMatrix and inputNumOfAtoms
        Returns: 
            boolean: True if the fractional coordinates can be read successfully, False if not 
        """
        #Using Gemmi struct class to use method get_all_unit_cell_sites
        struct = gemmi.make_small_structure_from_block(self.block)
        sites = struct.get_all_unit_cell_sites() #Extracts all atom coordinates from motif, no matter the symmetry
        frac = np.mod([[s.fract.x, s.fract.y, s.fract.z] for s in sites], 1)  #modded to make sure that they're in 
        types = np.array([s.element.name  for s in sites])

        # Validating coordinates. Any incorrect become Nan that we drop
        keep = np.flatnonzero(~np.isnan(frac).any(axis=1))
        if len(keep) < len(frac):
            print(f"{struct.name}: dropped {len(frac) - len(keep)} site(s) with missing coordinates")
        if not len(keep):
            print("no coordinates")
            self.errorMessage=f"{struct.name} has no valid coordinates"
            return False
        
        frac, types = frac[keep], types[keep] #Updates the list of fractional coordinates, removing those atoms that are missing
        self.inputNumOfAtoms = len(frac) #finds the number of atoms in the motif now
        self.inputFracCoordMatrix=np.transpose(frac)
        self.inputElementList = list(types)
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

    def extendFracCoords(self, numOfAtoms, extension, fracCoordMatrix, elementList):
        """Method that updates the list of fractional coordinates after extension
        Parameters: 
            numOfAtoms (integer): The number of atoms in the unit cell before extension
            extension (python list): Contains 3 elements that correspond to the 3 scale factors used for extension
            fracCoordMatrix (numpy array): 3 by (numOfAtoms) matrix containing the fractional coordinates
            elementList (python list): Contains all elements of the atoms in fracCoordMatrix (corresponding order) 
        Returns: 
            updated numOfAtoms, fracCoordMatrix, elementList
        """
        rtnFracCoordMatrix = fracCoordMatrix.copy()
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
        #now need to update the element list
        totalNoOfCopies = extension[0]*extension[1]*extension[2]
        rtnElementList = totalNoOfCopies * elementList.copy()
        return rtnNumOfAtoms, rtnFracCoordMatrix, rtnElementList

    def randomVectorInBall(self):
        """Method that uniformly samples the 3-ball
        Returns: 
            randomVector (numpy array with 3 elements)
        """
        #first uniformly sample the sphere
        randomVector = np.random.normal(0, 1, 3)
        randomVector = randomVector / np.linalg.norm(randomVector)
        scalar = random.uniform(0,1)
        randomVector = (scalar**(1/3)) * randomVector
        return randomVector

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
            translation = maxShift * self.randomVectorInBall()
            coordMatrix[:,position] = coordMatrix[:,position]+translation
        return coordMatrix

    def applyShiftsToAllAtoms(self,maxShift,numOfAtoms, euclideanCoordMatrix):
        """Method is same as applyShifts but applies the shifts to all of the atoms in the unit cell"""
        coordMatrix = euclideanCoordMatrix.copy()
        shiftMatrix = np.array([maxShift* self.randomVectorInBall() for i in range(numOfAtoms)]) #TIME CONSUMING
        shiftMatrix = np.transpose(shiftMatrix)
        rtnMatrix=coordMatrix+shiftMatrix
        return rtnMatrix

    def shuffleRows(self,fracCoordMatrix,elementList):
        """Method that shuffles the order of the atoms
        Parameters: 
            fracCoordMatrix (numpy array): 3 by (numOfAtoms) matrix containing the fractional coordinates
            elementList (python list): List of elements of all the atoms in the CIF
        Returns: 
            shuffled fracCoordMatrix, elementList (both shuffled in the same way so that element of each atom is correct)
        """
        # Array of coordinates
        fracCoordMatrixCopy=fracCoordMatrix.copy()
        elementListCopy = elementList.copy()
        indexPermutation = np.random.permutation(fracCoordMatrixCopy.shape[1]) # Generating a random permutation of the column indices
        shuffledFracCoordMatrix = fracCoordMatrixCopy[:, indexPermutation]  # 3. Use fancy indexing to shuffle the columns
        shuffledElementList = [elementListCopy[i] for i in indexPermutation]
        #Note will need to update the labels later
        return shuffledFracCoordMatrix, shuffledElementList
    
    


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
        """Method that sets class attributes document and block if you already have them to hand.
        Parameters: 
            cifDoc (Gemmi document)
            cifBlock (Gemmi Block list)
        """
        #
        self.document = cifDoc
        self.block =cifBlock

    def setTemplateManually(self, templatePath, blockNumber):
        """Method that reads the document and block from a template
        Parameters: 
            templatePath (string): filename of template
            blockNumber (integer): the block which contains the crystal in the template (usually 0)
        """
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
        """Method that updates the text after data_ in a file
        Parameters: 
            newBlockName (string): new blockname
            newCIFname (integer): filename of file that will be output
        """
        if newBlockName==None:
            self.block.name="disguised"
        else:
            self.block.name=newBlockName
        self.document.write_file(newCIFname)

    def updateCellAndAtoms(self, unitCellList, numOfAtoms, fracCoordMatrix, elementList, newCIFname):
        """Method that writes the new unit cell and fractional coordinates to the file
        Parameters: 
            unitCellList (Python list): contains the 6 unit cell data values
            numOfAtoms (integer): number of atoms (coordinates) in the motif
            fracCoordMatrix (numpy array): 3 rows, numOfAtoms columns containing the coordinates as floats
            elementList (Python list): Contains the elements of each coordinate. Has length numOfAtoms
            newCIFname (string): The name of the file we are writing the output to
        """
        unitCellDictionary = ['_cell_length_a', '_cell_length_b', '_cell_length_c', '_cell_angle_alpha', '_cell_angle_beta', '_cell_angle_gamma']
        for i in range(0,6):
            self.block.set_pair(unitCellDictionary[i], str(round(unitCellList[i],self.tolerance)))
        # Updating the volume
        newCell = gemmi.UnitCell(unitCellList[0],unitCellList[1],unitCellList[2],unitCellList[3],unitCellList[4],unitCellList[5])
        self.block.set_pair("_cell_volume",str(round(newCell.volume,self.tolerance)))

        # Updating the coordinates: 
        loop = self.block.find_loop_item('_atom_site_fract_x').loop #finding the loop in template that needs to be updated
        modFracCoordMatrix = fracCoordMatrix.copy() 
        modFracCoordMatrix = np.mod(modFracCoordMatrix, 1) # Moving all coordinates back into the unit cell
        rtnCoordTable = [] # Creating empty list that will contain all atom related stuff that will be written to file
    
        #Updating the labels
        labelList=[]
        elementSet = []
        noOfEachElement = []
        for i in range(numOfAtoms):
            element = elementList[i]
            if element not in elementSet:
                elementSet.append(element)
                noOfEachElement.append(1)
            else:
                elementIndex = elementSet.index(element)
                noOfEachElement[elementIndex] = noOfEachElement[elementIndex]+1
            labelList.append(element+str(noOfEachElement[elementSet.index(element)])) #updates the label itself
        rtnCoordTable.append(labelList)

        #Now setting the formula sum
        chem_formula_sum = "'"
        for j in range(len(elementSet)):
            chem_formula_sum=chem_formula_sum + elementSet[j]+str(noOfEachElement[j])+' '
        chem_formula_sum=chem_formula_sum + "'"
        self.block.set_pair("_chemical_formula_sum",chem_formula_sum)

        # Setting the 2nd column to the list of elements
        rtnCoordTable.append(elementList) 

        # Updating the x,y,z coordinates in the big table
        for i in range(3): 
            rtnCoordTable.append(list(map(str,list(map(round, modFracCoordMatrix[i].tolist(),[self.tolerance]*numOfAtoms))))) #Rounding and changing the numbers to strings

        # Setting symmetry_multiplicity to 1 for all atoms
        rtnCoordTable.append(['1']*numOfAtoms) 

        #Finally updating coordinate table to file
        loop.set_all_values(rtnCoordTable)
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

    def generateCif(self,inputUnitCellList, inputNumOfAtoms, inputFracCoordMatrix,inputElementList):
        if self.valid==True: #Checks if the input CIF passed the validation checks
            #Python is annoying and wants to do by reference. copy() should ensure that the original isn't being changed
            unitCellList = inputUnitCellList.copy()
            fracCoordMatrix = inputFracCoordMatrix.copy()
            numOfAtoms = inputNumOfAtoms
            elementList = inputElementList.copy()
            
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
                tempExtendOutputs = disguise.extendFracCoords(numOfAtoms, extension, fracCoordMatrix, elementList)
                numOfAtoms = tempExtendOutputs[0]
                fracCoordMatrix= tempExtendOutputs[1]
                elementList = tempExtendOutputs[2]
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

            if self.shuffleRows == True: 
                shuffleOutput = disguise.shuffleRows(fracCoordMatrix, elementList)
                fracCoordMatrix = shuffleOutput[0]
                elementList=shuffleOutput[1]
                self.generationInfo = self.generationInfo + "# The atom order was shuffled. \n"

            #write to the CIF
            outputCif.updateCellAndAtoms(unitCellList, numOfAtoms, fracCoordMatrix, elementList , self.newCIFname) # parameters: a 6 element list containing new unit cell values, the name of the new file

            outputCif.updateBlockName(self.newBlockName, self.newCIFname)
            outputCif.addMetaData(self.newCIFname,self.generationInfo)
            with open(self.newCIFname, 'r') as file:
                self.newCifContents = file.read()
            