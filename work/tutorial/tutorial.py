import matplotlib.pyplot as plt
import pandas as pd

fig = plt.figure(figsize=(8, 4))
ax = fig.subplots()
data = pd.read_csv("tutorial_data.csv")
t = data["time"].values
v = data["value"].values
ax.plot(t, v, "ko-", markersize=6)
ax.set_xlabel("時間 (s)", fontsize=20, labelpad=8)
ax.set_ylabel("デジタル出⼒値", fontsize=20, labelpad=8)
ax.tick_params(labelsize=16)
plt.tight_layout()
plt.savefig("result_tutorial.png")
plt.show()
