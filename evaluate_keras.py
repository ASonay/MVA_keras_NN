
# load and evaluate a saved model
import numpy as np
from keras.models import load_model
import ROOT as root
import mvasup
from array import array

#root_file='/home/asonay/ATLAS/MVA_result/SM4t-212560_ntuples/offline/1LOS/mvatuple_7ji2bi/4top_nlo_8ji3bi.root'
root_file='/home/asonay/ATLAS/MVA_result/SM4t-212560_ntuples/offline/1LOS/mvatuple_7ji2bi/ttbar_PhPy8_AFII_AllFilt_8ji3bi.root'
tree_name='nominal_Loose'
model_name='../MVA_Data/weights/model_1l_8ji3bi_0.h5'

norm=mvasup.Norm('strd_1l_8ji3bi','norm/')
variable_names = norm.Read()


f_read = root.TFile(root_file)
tree = f_read.Get(tree_name)
tree_f=[]
for i in range(len(variable_names)):
    tree_f.append(root.TTreeFormula('form_'+str(i),variable_names[i],tree))

n_entries = tree.GetEntries()
sample_size = len(tree_f)

X=[]
step=int(n_entries/20)

print('Reading ntuple..')
for i in range(n_entries):
    tree.GetEntry(i)
    x=[]
    for j,formula in enumerate(tree_f):
        x.append(formula.EvalInstance())
    X.append(x)
    if (i%step)==0:
        print (i,'/',n_entries,'events has been done...')
print('Finished..\n')

print ("Normalizing Inputs----------------------------------------")
X = np.array(X,dtype=float)
norm.Standardization(X)
print ("End of Normalization--------------------------------------\n")

# load model
model = load_model(model_name)
# summarize model.
model.summary()

Y=model.predict(X)

f_update = root.TFile(root_file,'update')
tree_update = f_update.Get(tree_name)

score = array('f', [ 0. ] )
score_branch = tree_update.Branch('NN_score',score,'NN_score/F')

print ('Updating ntuple---------------------------------------')
for i in range(n_entries):
    score[0]=Y[i]
    score_branch.Fill()

tree_update.Write(tree_name)
print('Finished..--------------------------------------------')
