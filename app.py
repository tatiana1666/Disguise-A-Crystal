from dash import Dash, dcc, html, Input, Output, callback, State, ctx
import base64
import algorithms as alg
import dash_daq as daq

app = Dash()

# Section for html layout ______________________________________________________________
app.layout = [
    html.Div(children=[ 
        html.H1(children='Disguise a Crystal'),
        html.Div(children=[
            html.H2(children='Introduction'),
            html.P(children='This is a web app that can generate a new-looking Crystallographic Information File (CIF) based on any input CIF! '),
            html.P(children='1) Use the on/off toggles to select which transformations you would like to apply to your input CIF.'),
            html.P(children='2) Scroll below the blue table and input your CIF in the "Input" column on the left-hand side. '),
            html.P(children='Please input your CIF in spacegroup P1 format, all other spacegroups will work in an upcoming update.'),
            html.P(children='3) Press the "Generate new CIF" button in the "Output" column.'),
            html.P(children='You can download the new CIF using the "Download CIF" button.'),
        ],id='intro'),
    ]),

    html.Div(children=[
        html.Div(children=['On/Off'],className='tableHeadings'),
        html.Div(children=['Transformation'],className='tableHeadings'),
        html.Div(children=['Advanced Information & Modifications'],className='tableHeadings'),
        html.Div(children=[
            daq.BooleanSwitch(className = 'toggleSwitch', id='extendSwitch', on=False,),
        ],className='box'),
        html.Div(children='Extend unit cell', className='transformationLabel'),
        html.Div(children=[
            html.Div(children=[
                html.Div(children=['Modify max extension scale factor:'],className='moreDetailsLabel'),
                html.Div(children=[
                    dcc.Input(className="inputNumber",id="inputUpperBoundExtension", type="number", value="2",min=1, max=4, step=1),
                ],),
            ],className='moreDetailsInputBox',),

            html.Div(children=[
                html.Div(children=['Scale factors used in generation (will display once file is generated):'],className='moreDetailsLabel'),
                html.Div(children=[
                    html.Div(children=['cell_length_a']),
                    html.Div(children=[],id="E1"),
                    html.Div(children=['cell_length_b']),
                    html.Div(children=[],id="E2"),
                    html.Div(children=['cell_length_c']),
                    html.Div(children=[],id="E3"),
                ],className='displaySfs',style={'background-color':'white','padding':'0px',}),
            ]),
        ],className='moreDetails'),

        html.Div(children=[
            daq.BooleanSwitch(className = 'toggleSwitch', id='shiftSwitch', on=False,),   
        ],className='toggleBox'),
        html.Div(children='Shift atoms slightly', className='transformationLabel'),
        html.Div(children=[
            html.Div(children=[
                html.Div(children=['Modify the upper bound of shift: (angstroms)'], className='moreDetailsLabel'),
                html.Div(children=[
                    dcc.Input(className="inputNumber",id="inputUpperBound", type="number", value="0.01",min=0, max=1,step=0.001,),
                ]),
            ],className='moreDetailsInputBox'),

            html.Div(children=[]),

            html.Div(children=[
                html.Div(children=['Toggle to shift all atoms:'], className='moreDetailsLabel'),
                html.Div(children=[
                    daq.BooleanSwitch(className = 'toggleSwitch', id='shiftAllSwitch', on=False,),
                ]),
            ],className='moreDetailsInputBox'),

            html.Div(children=[]),

            html.Div(children=[
                html.Div(children=['Or pick number of shifts:'], className='moreDetailsLabel'),
                html.Div(children=[
                    dcc.Input(className="inputNumber",id="inputNumOfShifts", type="number", value="0",min=0, max=999,),
                ],),
            ],className='moreDetailsInputBox'),            
        ],className='moreDetails'),

        html.Div(children=[
            daq.BooleanSwitch(className = 'toggleSwitch', id='rowShuffleSwitch', on=False),   
        ],className='toggleBox'),
        html.Div(children='Shuffle atom order', className='transformationLabel'),
        html.Div(children=[
            html.Div(children=[
                html.Div(children=[],className='moreDetailsLabel'),
                html.Div(children=[],className='moreDetailsInput')
            ],className='moreDetailsInputBox'),
            html.Div(children=[
                'Randomly shuffles the order of the atoms in the motif, then updates the labels.'
            ],className='moreDetailsLabel')
        ],className='moreDetails'),

        html.Div(children=[
            daq.BooleanSwitch(className = 'toggleSwitch', id='matrixSwitch', on=False,),
        ],className='toggleBox'),
        html.Div(children='Transform the basis',className='transformationLabel'),
        html.Div(children=[
            html.Div(children=[
                html.Div(children=['Modify the level of basis transformation:'], className='moreDetailsLabel'),
                html.Div(children=[
                    dcc.Slider(1, 5, 1,value=2,id='inputUpperBoundMatrix',),
                ]),
            ],className='moreDetailsInputBox'),
            html.Div(children=[
                'The matrix actually applied to the RHS of basis:',
                html.Div(children=[
                    html.Div('1', className='matrixBox', id='M1'),
                    html.Div('0', className='matrixBox', id='M2'),
                    html.Div('0', className='matrixBox', id='M3'),
                    html.Div('0', className='matrixBox', id='M4'),
                    html.Div('1', className='matrixBox', id='M5'),
                    html.Div('0', className='matrixBox', id='M6'),
                    html.Div('0', className='matrixBox', id='M7'),
                    html.Div('0', className='matrixBox', id='M8'),
                    html.Div('1', className='matrixBox', id='M9'),
                ],className='matrix'),
            ],className='moreDetailsLabel'),
        ],className='moreDetails'),

    ],className='topSection'),

    html.Div([
        #INPUT column
        html.Div([
            html.H2(children ='Input:'),
            # drag/upload button
            dcc.Upload(id='upload-data',
                children=html.Div(['Drag and Drop / ', html.A('Select Files')]),
                multiple=False # Allow multiple files to be uploaded or not 
            ),

            # Example file toggle
            html.Div(children=[
                html.Div(children=[
                    daq.BooleanSwitch(className = 'toggleSwitch', id='exampleSwitch1', on=False)
                ]),
                html.Div(children=[
                    'Or use an example crystal instead'
                ],className='exampleBoxLabel'),
            ],className='exampleBox'),

            # Example file toggle
            html.Div(children=[
                html.Div(children=[
                    daq.BooleanSwitch(className = 'toggleSwitch', id='exampleSwitch2', on=False,)
                ]),
                html.Div(children=[
                    'Or use a different example crystal (NaCl)'
                ],className='exampleBoxLabel'),
            ],className='exampleBox'),

            # Filename of input CIF
            html.Div(children = '',
            id='output-fileName'),

            # Input CIF contents
            html.Div(children = '',
            id='output-file'),
            
        ],className='column'),

        #OUTPUT column
        html.Div(children = [
            html.H2(children ='Output:'),

            html.Div(children=[
                html.Div(
                # button that will start the algorithm
                html.Button('Generate new CIF', id='generateCIFbutton', n_clicks=0),
                ),
                html.Div([
                    html.Button("Download CIF", id="btn-download"),
                    dcc.Download(id="download"),
                ]),
            ],className='generateSection'),

            html.Div([
                #Text box that inputs name of crystal within file
                html.Div(children=[
                    dcc.Textarea(id="inputName",placeholder="Rename block in CIF (optional)",),
                ],id = 'nameTextBoxLeft'),
                # button that submits data block name
                html.Div([ html.Button('Submit', id='inputNameSubmitBox', n_clicks=0),]),
                html.Div(id='indicator1',), 

            ],className = 'nameTextBox'),

            # div that contains contents of the output CIF
            html.Div( 
            id='output-new-Cif'),
                

        ],className='column'),
    
    ],id='bottomSection'),

    html.P(children='The crystal represented by the new CIF will be exactly the same geometrically even though the file might look completely different to the input file. '),
    html.Div(id='redundant1'),
    html.Div(id='redundant2'),
    html.Div(id='redundant3'),
]

# Section for callbacks (page behaviour) __________________________________________________

# Uploading CIF:
def parse_contents(filecontents):
    try:
        content=""
        add=False
        for line in filecontents:
            if add==True:
                if line.strip():
                    content=content+line
            if line==",":
                add=True
        content = base64.b64decode(content.encode("ascii")).decode("ascii")
    except UnicodeDecodeError:
        content = False
    return content

#Callback for displaying filename
@callback(  Output('output-fileName', 'children'),
            Input('exampleSwitch1', 'on'),
            Input('exampleSwitch2', 'on'),
            Input('upload-data', 'contents'),
            State('upload-data', 'filename')
            )
def update_output(exampleswitch1,exampleSwitch2, filecontents, filename): # Outputting the filename
    if exampleswitch1==True:
        return "File Name: example_T2Crystal.cif "
    elif exampleSwitch2==True:
        return "File Name: example_NaCl.cif "
    elif filecontents is not None:
        return "File Name: {} ".format(filename)

#Callback for displaying the input file contents
@callback(  Output('output-file', 'children'),
            Input('exampleSwitch1', 'on'),
            Input('exampleSwitch2', 'on'),
            Input('upload-data', 'contents'),
            State('upload-data', 'filename'),
            )
def update_output(exampleSwitch1,exampleSwitch2,filecontents,filename): # Outputting the file contents
    readCif = alg.cifReaderClass()
    mainInstance=alg.main()
    if exampleSwitch1 == True: 
        validCif = readCif.readInputCIF('example_T2Crystal.cif')
        if validCif==True:
            mainInstance.valid=True
            with open('example_T2Crystal.cif', 'r') as file:
                exampleFile = file.read()
            return "CIF contents: \n {}".format(exampleFile)
        else:
            mainInstance.valid=False
            return "Error: \n {}".format(validCif)
    elif exampleSwitch2 == True: 
        validCif = readCif.readInputCIF('example_NaCl.cif')
        if validCif==True:
            mainInstance.valid=True
            with open('example_NaCl.cif', 'r') as file:
                exampleFile = file.read()
            return "CIF contents: \n {}".format(exampleFile)
        else:
            mainInstance.valid=False
            return "Error: \n {}".format(validCif)
    elif filecontents is not None:
        contents = parse_contents(filecontents)
        if contents == False:
            mainInstance.valid=False
            return "Please ensure file has .cif extension and uses ASCII"
        f = open(filename, "w")
        f.write(contents)
        f.close()
        validCif = readCif.readInputCIF(filename)
        if validCif == True:
            mainInstance.valid=True
            return "CIF contents: \n {}".format(contents)
        else:
            mainInstance.valid=False
            return "Error: \n {}".format(validCif)


# Download file callback
@callback(
    Output("download", "data"),
    Input("btn-download", "n_clicks"),
    State("output-new-Cif","children"),
    prevent_initial_call=True,
)
def func(n_clicks,newCifContents):
    return dict(content=newCifContents, filename="disguisedCrystal.cif")

#Change name inside CIF text box callbacks
@callback(
    Output('indicator1', 'style'),
    Output('output-new-Cif', 'children',allow_duplicate=True),
    Input('inputNameSubmitBox', 'n_clicks'),
    Input('inputName', 'value'),
    State('inputName', 'value'),
    State('output-new-Cif', 'children'),
    prevent_initial_call=True,
)
def change_button_style(n_clicks,inputName1,inputName2,cifContents):
    #please note that this code depends on the new CIF being called "newCif.cif" and the data being in the first block
    if n_clicks > 0 and "inputNameSubmitBox" == ctx.triggered_id and cifContents!="A valid CIF has not been input":
        outputCifInstance1=alg.outputCifClass()
        outputCifInstance1.setTemplateManually("newCif.cif", 0)
        outputCifInstance1.updateBlockName(inputName2, "newCif.cif")
        with open("newCif.cif", 'r') as file:
                newCifContents = file.read()
        return {'background-color': '#85b088'},newCifContents
    else:
        return {'background-color':'#d3d3d3'},cifContents
    
# Callbacks that ensures consistency when picking how many atoms to shift
@callback(
    Output('shiftAllSwitch', 'on'),
    Input('shiftSwitch', 'on'),
    Input('inputNumOfShifts', 'value'),
    prevent_initial_call=True,
)
def change_button_style(switch,value):
    if switch==True and int(value)==0:
        return True
    else:
        return False

# Generate new CIF button
@callback(
    Output('output-new-Cif', 'children',allow_duplicate=True),
    Output('M1', 'children'),
    Output('M4', 'children'),
    Output('M7', 'children'),
    Output('M2', 'children'),
    Output('M5', 'children'),
    Output('M8', 'children'),
    Output('M3', 'children'),
    Output('M6', 'children'),
    Output('M9', 'children'),
    Output('E1', 'children'),
    Output('E2', 'children'),
    Output('E3', 'children'),
    Input('generateCIFbutton', 'n_clicks'),
    State('exampleSwitch1','on'),
    State('exampleSwitch2','on'),
    State('upload-data', 'contents'),
    State('upload-data', 'filename'),
    State('matrixSwitch','on'),
    State('extendSwitch','on'),
    State('rowShuffleSwitch','on'),
    State('shiftSwitch','on'),
    State('shiftAllSwitch','on'),
    State('inputNumOfShifts','value'),
    State('inputUpperBound','value'),
    State('inputUpperBoundExtension','value'), 
    State('inputUpperBoundMatrix','value'),    
    prevent_initial_call=True,
)
def update_output(n_clicks_gen,exampleSwitch1,exampleSwitch2, cifContents, cifFilename, matrixSwitch,extendSwitch,rowShuffleSwitch, shiftSwitch,shiftAllSwitch,inputNumOfShifts,inputUpperBound,inputUpperBoundExtension,inputUpperBoundMatrix):
    mainInstance1=alg.main()
    readCifInstance1 = alg.cifReaderClass()
    # Code for inputting CIF
    if exampleSwitch1 == True: 
        mainInstance1.valid = readCifInstance1.readInputCIF('example_T2Crystal.cif')
    elif exampleSwitch2 ==True:
        mainInstance1.valid = readCifInstance1.readInputCIF('example_NaCl.cif')
    elif cifContents is not None: # Subroutine runs if file is uploaded
        contents = parse_contents(cifContents) # Uploaded file must first be parsed before it is processed
        if contents == False:
            mainInstance1.valid=False
        else:
            f = open(cifFilename, "w")
            f.write(contents)
            f.close()
            mainInstance1.valid = readCifInstance1.readInputCIF(cifFilename)
    # Parameters are updated based on states of the toggle switches:
    if matrixSwitch == True: 
        mainInstance1.transformBasis = True
        mainInstance1.upperBoundMatrix=int(inputUpperBoundMatrix)
    else:
        mainInstance1.transformBasis=False
    if extendSwitch == True: 
        mainInstance1.extendBasis = True
        mainInstance1.upperBoundExtension = int(inputUpperBoundExtension)
    else:
        mainInstance1.extendBasis=False
    if shiftSwitch == True: 
        mainInstance1.shiftAtoms = True
        mainInstance1.numOfShifts = inputNumOfShifts
        mainInstance1.maxShift = float(inputUpperBound)
        mainInstance1.shiftAllAtoms = shiftAllSwitch
    else:
        mainInstance1.shiftAtoms=False
    if rowShuffleSwitch == True:
        mainInstance1.shuffleRows=True
    else:
        mainInstance1.shuffleRows=False
    # Then the new file is generated:
    mainInstance1.generateCif(readCifInstance1.inputUnitCell, readCifInstance1.inputNumOfAtoms, readCifInstance1.inputFracCoordMatrix, readCifInstance1.inputCoordTable,readCifInstance1.inputCoordTableTags)
    # Update the outputs to display details about the generation:
    randomMatrix = mainInstance1.randomMatrix.tolist()
    return mainInstance1.newCifContents,randomMatrix[0][0],randomMatrix[0][1],randomMatrix[0][2],randomMatrix[1][0],randomMatrix[1][1],randomMatrix[1][2],randomMatrix[2][0],randomMatrix[2][1],randomMatrix[2][2],mainInstance1.extensionSfs[0],mainInstance1.extensionSfs[1],mainInstance1.extensionSfs[2]
    

if __name__ == "__main__":
    app.run(debug=True)