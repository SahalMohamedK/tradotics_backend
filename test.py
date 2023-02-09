import pandas as pd

df = pd.read_csv('media/output_trades/ff8eb038ce0de96f8ade9f0cea0e0339.csv')
df.loc[1, 'setup']= ''
print(df.loc[1, 'setup'] == '')