#include "TCut.h"
#include "inc/ReadTree.hh"

using namespace std;

struct TrainingVars
{
  vector<string> variables;
  string weight_signal;
  string weight_background;
};

TrainingVars ReadVariables(string variable_list){
  ifstream in(variable_list);
  string str;
  TrainingVars GetVars;

  if (in.fail()) {cout << "Your variable list is missing!\n"; exit(0);}
  
  while (in >> str){
    if (str.compare("var:")==0){
      in >> str;
      GetVars.variables.push_back(str);
    }
    else if (str.compare("sgw:")==0){
      in >> str;
      GetVars.weight_signal=str;
    }
    else if (str.compare("bgw:")==0){
      in >> str;
      GetVars.weight_background=str;
    }
    else
      cout << "Your file is badly formatted.." << endl;
  }

  return GetVars;
}

void ntuple_to_csv(string ntuple_sig = "/home/asonay/ATLAS/MVA_result/SM4t-212560_ntuples/offline/1LOS/mvatuple_7ji2bi/4top_nlo_8ji3bi.root",
		   string ntuple_bkg = "/home/asonay/ATLAS/MVA_result/SM4t-212560_ntuples/offline/1LOS/mvatuple_7ji2bi/ttbar_PhPy8_AFII_AllFilt_8ji3bi.root",
		   string tree_name_sig = "nominal_Loose",
		   string tree_name_bkg = "nominal_Loose",
		   string variable_list = "list/VariableList.txt",
		   string output_file_name = "MVA_Data/data/training_1l_8ji3bi.csv"
		   )
{
  

  TrainingVars GetVars = ReadVariables(variable_list);
  vector<string> variables = GetVars.variables;
  string weight_signal = GetVars.weight_signal;
  string weight_background = GetVars.weight_background;

  TFile *f_sig = new TFile(ntuple_sig.c_str());
  TFile *f_bkg = new TFile(ntuple_bkg.c_str());

  TTree *tr_sig = (TTree*)f_sig->Get(tree_name_sig.c_str());
  TTree *tr_bkg = (TTree*)f_bkg->Get(tree_name_bkg.c_str());

  unsigned n_sig = tr_sig->GetEntries();
  unsigned n_bkg = tr_bkg->GetEntries();


  ReadTree sig("Data_sig",tr_sig,variables);
  ReadTree bkg("Data_bkg",tr_bkg,variables);

  sig.SetSingleVariable(weight_signal);
  bkg.SetSingleVariable(weight_background);


  vector<double> var;
  vector<int> label;
  double w;
  vector<int> cont_sig(6,-1);
  vector<int> cont_bkg(6,-1);
  vector<string> cond = {"nJets>=10&&nBTags_MV2c10_70>=4",
			 "nJets>=10&&nBTags_MV2c10_70==3",
			 "nJets==9&&nBTags_MV2c10_70>=4",
			 "nJets==9&&nBTags_MV2c10_70==3",
			 "nJets==8&&nBTags_MV2c10_70>=4",
			 "nJets==8&&nBTags_MV2c10_70==3",
  };

  ofstream myfile;
  myfile.open (output_file_name);

  myfile << "id" << ",";
  for (int i=0;i<variables.size();i++)
    myfile << variables[i] << ",";
   
  myfile << "weights" << ",";
  for (int i=0;i<12;i++)
    myfile << "label_"<< i+1 << ",";
  myfile << "label" << endl;

    
  int cous=0,coub=0;
  for (int i=0;i<n_sig+n_bkg;i++){
      for (int out=0;out<6;out++){

	cout << "CONDITION : " << cond[out] << endl;
	
	cont_sig[out] = sig.GetConditionalIndex(cond[out],cont_sig[out]+1);
	var = sig.GetInput(cont_sig[out]);
	w = sig.GetInputSingle(cont_sig[out]);
	
	for (int out_layer=0;out_layer<12;out_layer++){
	  if (out_layer==out)
	    label.push_back(1);
	  else
	    label.push_back(0);
	}

	for (auto x : var) cout << x << " ";
	cout << "" << endl;
	for (auto x : label) cout << x << " ";
	cout << w << " s   ||" << cont_sig[out]<< endl;
	
	myfile << i << ",";
	for (auto x : var) myfile << x << ",";
	myfile << w << ",";
	for (auto x : label) myfile << x << ",";
	myfile << "s" << endl;
	label.clear();
	
	cont_bkg[out] = bkg.GetConditionalIndex(cond[out],cont_bkg[out]+1);
	var = bkg.GetInput(cont_bkg[out]);
	w = bkg.GetInputSingle(cont_bkg[out]);
	
	for (int out_layer=0;out_layer<12;out_layer++){
	  if (out_layer==11-out)
	    label.push_back(1);
	  else
	    label.push_back(0);
	}
	
	for (auto x : var) cout << x << " ";
	cout << "" << endl;
	for (auto x : label) cout << x << " ";
	cout << w << " b   ||" << cont_bkg[out]<< endl;
	
	myfile << i << ",";
	for (int j=0;j<variables.size();j++)
	  myfile << var[j] << ",";
	myfile << w << ",";
	for (auto x : label) myfile << x << ",";
	myfile << "b" << endl;
	label.clear();
	
   
	if (cont_sig[out]>=n_sig) cont_sig[out]=-1;
	if (cont_bkg[out]>=n_bkg) cont_bkg[out]=-1;
      }
      
  }
  
  myfile.close();


}
