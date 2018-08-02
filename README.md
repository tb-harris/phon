```
th preprocess.lua -data_type monotext -train phon6/TRAIN.txt -valid phon6/VAL.txt -save_data phon6/data -time_shift_feature false

th train.lua -model_type lm -rnn_size 300 -word_vec_size 50 -feat_vec_exponent .82 -data phon6/data-train.t7 -save_model phon6/model -log_file phon6/log

th tools/extract_embeddings_feat.lua -model phon6/model_epoch13_12.04.t7 -output_dir phon6
```
