import backtrader as bt

class AccumulativeSwingIndex(bt.Indicator): 
    lines = ("asi",)
    params = (
        ("T_percent", 0.02),
    )

    def __init__(self):
        self.lines.asi = bt.LineNum(0.0)
        self.addminperiod(2)

    def calculate_R_value(self, H, Cy, L, Oy):
        option1 = H - Cy
        option2 = L - Cy
        option3 = H - L
        max_option = max(option1, option2, option3)

        if max_option == option1:
            R = (H - Cy) - 0.5 * (L - Cy) + 0.25 * (Cy - Oy)
        elif max_option == option2:
            R = (L - Cy) - 0.5 * (H - Cy) + 0.25 * (Cy - Oy)
        else:
            R = (H - L) + 0.25 * (Cy - Oy)

        return R

    def next(self) -> None:
        C = self.data.close[0]
        Cy = self.data.close[-1]
        Open = self.data.open[0]
        Oy = self.data.open[-1]
        H = self.data.high[0]
        Hy = self.data.high[-1]
        L = self.data.low[0]
        Ly = self.data.low[-1]

        K = max(Hy - C, Ly - C)

        R = self.calculate_R_value(H=H, Cy=Cy, L=L, Oy=Oy)
        T = Cy * self.p.T_percent
        
        if R == 0 or T == 0:
            SI = 0.0
        else:
            numerator = Cy - C + 0.5 * (Cy - Oy) + 0.25 * (C - Open)
            SI = 50 * (numerator / R) * (K / T)

        self.lines.asi[0] = self.lines.asi[-1] + SI