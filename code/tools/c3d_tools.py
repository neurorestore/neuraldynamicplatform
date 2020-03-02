import btk

def read_c3d(fileName,kinLabels,emgLabels,stimLabel,printKinLabelsFlag=False,printEmgLabelsFlag=False):
    # build a btk reader object
    reader = btk.btkAcquisitionFileReader()
    # set a filename to the reader
    print fileName
    reader.SetFilename(fileName)
    reader.Update()
    # acq is the btk aquisition object
    acq = reader.GetOutput()

    # get the point frequency
    pointFrequency = acq.GetPointFrequency()
    # Build kin dictionary
    if printKinLabelsFlag: printKinLabels(acq)
    kin = {}
    for kinLabel in kinLabels:
        point = acq.GetPoint(kinLabel)
        kin[kinLabel] = point.GetValues() # return a numpy array of nrows and 3 columns

    # get the analog frequency
    analogFrequency = acq.GetAnalogFrequency()
    # Build emg dictionary
    if printEmgLabelsFlag: printEmgLabels(acq)
    emg = {}
    for emgLabel in emgLabels:
        analog = acq.GetAnalog(emgLabel)
        emg[emgLabel] = analog.GetValues() # return a numpy array of nrows and 3 columns

    analog = acq.GetAnalog(stimLabel)
    stim = analog.GetValues().astype(bool)

    return kin,emg,stim,pointFrequency,analogFrequency

def printKinLabels(acq):
    read = 1
    while read:
        try:
            print acq.GetPoint(read-1).GetLabel()
            read+=1
        except:read=False

def printEmgLabels(acq):
    read = 1
    while read:
        try:
            print acq.GetAnalog(read-1).GetLabel()
            read+=1
        except:read=False
