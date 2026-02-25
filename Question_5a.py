import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import math
from datetime import datetime, timedelta
from itertools import combinations, permutations
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TouristSpot:
    def __init__(self, name, latitude, longitude, entry_fee, open_time, close_time, tags):
        self.name, self.latitude, self.longitude = name, latitude, longitude
        self.entry_fee, self.open_time, self.close_time = entry_fee, open_time, close_time
        self.tags = tags if isinstance(tags, list) else tags.split(';')
    def __repr__(self): return f"TouristSpot({self.name})"

class HeuristicOptimizer:
    def __init__(self, spots, prefs):
        self.spots, self.total_time, self.max_budget = spots, prefs['total_time'], prefs['max_budget']
        self.interest_tags, self.start_time = prefs['interest_tags'], prefs.get('start_time', '09:00')
        self.itinerary, self.total_cost, self.time_spent = [], 0, 0
        self.current_time = datetime.strptime(self.start_time, "%H:%M")
        self.current_location, self.explanations = None, []

    def _parse(self, t): return datetime.strptime(t, "%H:%M")
    def _str(self, t): return t.strftime("%H:%M")

    def distance(self, a, b):
        if a is None: return 0
        return math.sqrt((b.latitude-a.latitude)**2 + (b.longitude-a.longitude)**2) * 111

    def travel_time(self, d): return d / 30 if d > 0 else 0

    def visit_duration(self, spot):
        if any(t in spot.tags for t in ['nature', 'adventure']): return 2.0
        if any(t in spot.tags for t in ['religious', 'heritage']): return 1.0
        return 1.5

    def score(self, spot, visited):
        if spot in visited: return -1
        if self.total_cost + spot.entry_fee > self.max_budget: return -1
        d = self.distance(self.current_location, spot)
        tt, vd = self.travel_time(d), self.visit_duration(spot)
        if self.time_spent + tt + vd > self.total_time: return -1
        arr = self.current_time + timedelta(hours=tt)
        op, cl = self._parse(spot.open_time), self._parse(spot.close_time)
        if arr.time() < op.time():
            wait = (datetime.combine(arr.date(), op.time()) - arr).seconds / 3600
            arr, tt = datetime.combine(arr.date(), op.time()), tt + wait
            if self.time_spent + tt + vd > self.total_time: return -1
        if arr.time() >= cl.time(): return -1
        int_s = sum(1 for t in spot.tags if t.lower() in [x.lower() for x in self.interest_tags])
        int_s = int_s / len(self.interest_tags) if self.interest_tags else 0
        bud_s = 1 - (spot.entry_fee / self.max_budget) if self.max_budget > 0 else 0
        prox_s = 1 - min(d / 50, 1)
        time_s = (self.total_time - self.time_spent - tt - vd) / self.total_time if self.total_time > 0 else 0
        return 0.40*int_s + 0.20*bud_s + 0.25*prox_s + 0.15*time_s

    def optimize(self):
        visited, i = set(), 0
        while True:
            i += 1
            best, best_s = None, -1
            for spot in self.spots:
                s = self.score(spot, visited)
                if s > best_s: best_s, best = s, spot
            if best is None or best_s == -1: break
            d = self.distance(self.current_location, best)
            tt, vd = self.travel_time(d), self.visit_duration(best)
            arr = self.current_time + timedelta(hours=tt)
            op = self._parse(best.open_time)
            if arr.time() < op.time():
                wait = (datetime.combine(arr.date(), op.time()) - arr).seconds / 3600
                arr, tt = datetime.combine(arr.date(), op.time()), tt + wait
            dep = arr + timedelta(hours=vd)
            reasons = []
            matches = [t for t in best.tags if t.lower() in [x.lower() for x in self.interest_tags]]
            if matches: reasons.append(f"matches interests: {', '.join(matches)}")
            if best.entry_fee < self.max_budget * 0.3: reasons.append("budget-friendly")
            if d < 5: reasons.append("nearby location")
            exp = f"Step {i}: Selected '{best.name}' (Score: {best_s:.3f}) - {', '.join(reasons) or 'best available option'}"
            self.itinerary.append({'spot': best, 'arrival_time': self._str(arr), 'departure_time': self._str(dep),
                'travel_time': round(tt,2), 'visit_duration': round(vd,2), 'distance_from_previous': round(d,2),
                'cost': best.entry_fee, 'score': round(best_s,3), 'explanation': exp})
            self.explanations.append(exp)
            visited.add(best); self.current_location = best; self.current_time = dep
            self.total_cost += best.entry_fee; self.time_spent += tt + vd
        return {'itinerary': self.itinerary, 'total_cost': self.total_cost, 'total_time': round(self.time_spent,2),
                'spots_visited': len(self.itinerary), 'explanations': self.explanations,
                'budget_remaining': self.max_budget - self.total_cost,
                'time_remaining': round(self.total_time - self.time_spent, 2)}

class BruteForceOptimizer:
    def __init__(self, spots, prefs):
        self.spots, self.total_time, self.max_budget = spots, prefs['total_time'], prefs['max_budget']
        self.interest_tags, self.start_time = prefs['interest_tags'], prefs.get('start_time', '09:00')

    def distance(self, a, b):
        if a is None: return 0
        return math.sqrt((b.latitude-a.latitude)**2 + (b.longitude-a.longitude)**2) * 111

    def eval_path(self, path):
        loc, t = None, datetime.strptime(self.start_time, "%H:%M")
        cost, ts, matches = 0, 0, 0
        for spot in path:
            d = self.distance(loc, spot); tt = d / 30; ts += tt + 1.5; cost += spot.entry_fee
            if ts > self.total_time or cost > self.max_budget: return False, -1, 0, 0
            arr = t + timedelta(hours=tt)
            cl = datetime.strptime(spot.close_time, "%H:%M")
            if arr.time() >= cl.time(): return False, -1, 0, 0
            matches += sum(1 for tag in spot.tags if tag.lower() in [x.lower() for x in self.interest_tags])
            loc, t = spot, arr + timedelta(hours=1.5)
        return True, len(path)*10 + matches*5 - cost*0.01, cost, ts

    def optimize(self):
        best_path, best_s, best_c, best_t = None, -1, 0, 0
        for size in range(len(self.spots), 0, -1):
            for subset in combinations(self.spots, size):
                for path in permutations(subset):
                    ok, s, c, t = self.eval_path(path)
                    if ok and s > best_s: best_s, best_path, best_c, best_t = s, path, c, t
            if best_path: break
        return {'path': best_path, 'score': best_s, 'total_cost': best_c,
                'total_time': round(best_t,2), 'spots_visited': len(best_path) if best_path else 0}

SPOTS_DATA = [
    {"name":"Pashupatinath Temple","latitude":27.7104,"longitude":85.3488,"entry_fee":100,"open_time":"06:00","close_time":"18:00","tags":["culture","religious"]},
    {"name":"Swayambhunath Stupa","latitude":27.7149,"longitude":85.2906,"entry_fee":200,"open_time":"07:00","close_time":"17:00","tags":["culture","heritage"]},
    {"name":"Garden of Dreams","latitude":27.7125,"longitude":85.3170,"entry_fee":150,"open_time":"09:00","close_time":"21:00","tags":["nature","relaxation"]},
    {"name":"Chandragiri Hills","latitude":27.6616,"longitude":85.2458,"entry_fee":700,"open_time":"09:00","close_time":"17:00","tags":["nature","adventure"]},
    {"name":"Kathmandu Durbar Square","latitude":27.7048,"longitude":85.3076,"entry_fee":100,"open_time":"10:00","close_time":"17:00","tags":["culture","heritage"]},
    {"name":"Boudhanath Stupa","latitude":27.7215,"longitude":85.3617,"entry_fee":150,"open_time":"06:00","close_time":"19:00","tags":["culture","religious"]},
]

class TouristOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tourist Spot Optimizer - DSA Coursework")
        self.root.geometry("1200x800")
        self.spots = [TouristSpot(**s) for s in SPOTS_DATA]
        self.heuristic_result = self.bruteforce_result = None
        self._build_gui()

    def _build_gui(self):
        mf = ttk.Frame(self.root, padding="10")
        mf.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1); self.root.rowconfigure(0, weight=1)
        mf.columnconfigure(1, weight=1); mf.rowconfigure(0, weight=1)
        self._input_panel(mf); self._results_panel(mf)

    def _input_panel(self, parent):
        f = ttk.LabelFrame(parent, text="User Preferences", padding="10")
        f.grid(row=0, column=0, sticky="nsew", padx=5)
        fields = [("Total Time Available (hours):", "8"), ("Maximum Budget (NPR):", "1500"), ("Start Time (HH:MM):", "09:00")]
        self.time_var, self.budget_var, self.start_time_var = (tk.StringVar(value=v) for _, v in fields)
        for i, ((lbl, _), var) in enumerate(zip(fields, [self.time_var, self.budget_var, self.start_time_var])):
            ttk.Label(f, text=lbl).grid(row=i, column=0, sticky=tk.W, pady=5)
            ttk.Entry(f, textvariable=var, width=20).grid(row=i, column=1, pady=5)
        ttk.Label(f, text="Interest Tags:").grid(row=3, column=0, sticky=tk.W, pady=5)
        tf = ttk.Frame(f); tf.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        self.tag_vars = {}
        for i, tag in enumerate(["culture","nature","religious","heritage","adventure","relaxation"]):
            var = tk.BooleanVar(value=(tag in ["culture","nature"]))
            self.tag_vars[tag] = var
            ttk.Checkbutton(tf, text=tag.capitalize(), variable=var).grid(row=i//2, column=i%2, sticky=tk.W)
        ttk.Label(f, text="Available Tourist Spots:").grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(15,5))
        st = scrolledtext.ScrolledText(f, height=10, width=40)
        st.grid(row=6, column=0, columnspan=2, pady=5)
        for s in self.spots:
            st.insert(tk.END, f"• {s.name}\n  Fee: NPR {s.entry_fee} | Hours: {s.open_time}-{s.close_time}\n  Tags: {', '.join(s.tags)}\n\n")
        st.config(state=tk.DISABLED)
        ttk.Button(f, text="Generate Optimal Itinerary", command=self.run_optimization).grid(row=7, column=0, columnspan=2, pady=15)
        ttk.Button(f, text="Compare with Brute-Force (Small Dataset)", command=self.run_comparison).grid(row=8, column=0, columnspan=2, pady=5)

    def _results_panel(self, parent):
        rf = ttk.LabelFrame(parent, text="Results & Visualization", padding="10")
        rf.grid(row=0, column=1, sticky="nsew", padx=5)
        rf.columnconfigure(0, weight=1); rf.rowconfigure(0, weight=1)
        self.nb = ttk.Notebook(rf)
        self.nb.grid(row=0, column=0, sticky="nsew")
        def tab(label):
            fr = ttk.Frame(self.nb); self.nb.add(fr, text=label)
            t = scrolledtext.ScrolledText(fr, height=30, width=70, wrap=tk.WORD)
            t.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            return fr, t
        _, self.itin_txt = tab("Suggested Itinerary")
        self.map_frame = ttk.Frame(self.nb); self.nb.add(self.map_frame, text="Map View")
        _, self.exp_txt = tab("Decision Explanation")
        _, self.cmp_txt = tab("Algorithm Comparison")

    def _get_prefs(self):
        tags = [t for t, v in self.tag_vars.items() if v.get()]
        if not tags: messagebox.showwarning("Input Error", "Please select at least one interest tag!"); return None
        return {'total_time': float(self.time_var.get()), 'max_budget': float(self.budget_var.get()),
                'interest_tags': tags, 'start_time': self.start_time_var.get()}

    def run_optimization(self):
        try:
            prefs = self._get_prefs()
            if not prefs: return
            t0 = time.time()
            opt = HeuristicOptimizer(self.spots, prefs)
            self.heuristic_result = opt.optimize()
            et = time.time() - t0
            self._show_itinerary(self.heuristic_result, et)
            self._show_explanation(self.heuristic_result)
            self._show_map(self.heuristic_result)
            messagebox.showinfo("Success", f"Itinerary generated!\nSpots: {self.heuristic_result['spots_visited']}\nTime: {et:.4f}s")
        except ValueError as e: messagebox.showerror("Input Error", f"Invalid input: {e}")
        except Exception as e: messagebox.showerror("Error", str(e))

    def _write(self, widget, text, clear=True):
        widget.config(state=tk.NORMAL)
        if clear: widget.delete(1.0, tk.END)
        widget.insert(tk.END, text)
        widget.config(state=tk.DISABLED)

    def _show_itinerary(self, r, et):
        lines = ["="*70+"\n","OPTIMIZED TOURIST ITINERARY - HEURISTIC ALGORITHM\n","="*70+"\n\n",
                 f"SUMMARY\n{'─'*70}\n",
                 f"Total Spots Visited: {r['spots_visited']}\nTotal Cost: NPR {r['total_cost']:.2f}\n",
                 f"Total Time: {r['total_time']:.2f} hours\nBudget Remaining: NPR {r['budget_remaining']:.2f}\n",
                 f"Time Remaining: {r['time_remaining']:.2f} hours\nExecution Time: {et:.4f} seconds\n\n",
                 f"{'─'*70}\n\nDETAILED ITINERARY\n{'─'*70}\n\n"]
        for i, e in enumerate(r['itinerary'], 1):
            s = e['spot']
            lines += [f"Stop {i}: {s.name}\n",
                      f"  Location: ({s.latitude:.4f}, {s.longitude:.4f})\n",
                      f"  Arrival: {e['arrival_time']} | Departure: {e['departure_time']}\n",
                      f"  Visit Duration: {e['visit_duration']} hrs | Travel Time: {e['travel_time']} hrs ({e['distance_from_previous']:.2f} km)\n",
                      f"  Entry Fee: NPR {e['cost']} | Tags: {', '.join(s.tags)} | Score: {e['score']:.3f}\n\n"]
        self._write(self.itin_txt, "".join(lines))

    def _show_explanation(self, r):
        lines = ["="*70+"\nALGORITHM DECISION EXPLANATION\n"+"="*70+"\n\n",
                 "GREEDY HEURISTIC ALGORITHM\n"+"─"*70+"\n\n",
                 "Score = 0.40×InterestMatch + 0.20×BudgetFit + 0.25×Proximity + 0.15×TimeWindow\n\n",
                 "  • Interest Match (40%): Spot tags vs user preferences\n",
                 "  • Budget Fit (20%): Cost efficiency within budget\n",
                 "  • Proximity (25%): Distance from current location\n",
                 "  • Time Window (15%): Opening hours & time limits\n\n",
                 "─"*70+"\nSTEP-BY-STEP DECISIONS:\n"+"─"*70+"\n\n"]
        for e in r['explanations']: lines.append(f"✓ {e}\n\n")
        lines += ["\n"+"─"*70+"\nCOMPLEXITY ANALYSIS:\n"+"─"*70+"\n\n",
                  "Time Complexity: O(n²) | Space Complexity: O(n)\n"]
        self._write(self.exp_txt, "".join(lines))

    def _show_map(self, r):
        for w in self.map_frame.winfo_children(): w.destroy()
        fig = Figure(figsize=(8,6)); ax = fig.add_subplot(111)
        if r['itinerary']:
            lats = [e['spot'].latitude for e in r['itinerary']]
            lons = [e['spot'].longitude for e in r['itinerary']]
            names = [e['spot'].name for e in r['itinerary']]
            ax.scatter(lons, lats, c='red', s=100, zorder=5)
            ax.plot(lons, lats, 'b-', linewidth=2, alpha=0.6, zorder=3)
            for i, (lon, lat, name) in enumerate(zip(lons, lats, names), 1):
                ax.annotate(f"{i}. {name}", xy=(lon,lat), xytext=(5,5), textcoords='offset points',
                            fontsize=8, bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
            ax.scatter(lons[0], lats[0], c='green', s=200, marker='*', zorder=6, label='Start')
            ax.scatter(lons[-1], lats[-1], c='blue', s=200, marker='s', zorder=6, label='End')
            ax.legend()
        else:
            ax.text(0.5, 0.5, 'No itinerary to display', ha='center', va='center', transform=ax.transAxes, fontsize=14)
        ax.set_xlabel('Longitude'); ax.set_ylabel('Latitude'); ax.set_title('Tourist Spot Visit Sequence'); ax.grid(True, alpha=0.3)
        FigureCanvasTkAgg(fig, master=self.map_frame).get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def run_comparison(self):
        try:
            prefs = self._get_prefs()
            if not prefs: return
            small = self.spots[:5]
            t0 = time.time(); hr = HeuristicOptimizer(small, prefs).optimize(); ht = time.time()-t0
            t0 = time.time(); br = BruteForceOptimizer(small, prefs).optimize(); bt = time.time()-t0
            sp = bt/ht if ht > 0 else 0
            acc = (hr['spots_visited'] / max(br['spots_visited'],1)) * 100
            lines = ["="*70+"\nALGORITHM COMPARISON: HEURISTIC vs BRUTE-FORCE\n"+"="*70+"\n\n",
                     "Dataset: First 5 tourist spots\n\n","─"*70+"\n",
                     f"{'Metric':<30} {'Heuristic':<20} {'Brute-Force':<20}\n","─"*70+"\n",
                     f"{'Spots Visited':<30} {hr['spots_visited']:<20} {br['spots_visited']:<20}\n",
                     f"{'Total Cost (NPR)':<30} {hr['total_cost']:<20.2f} {br['total_cost']:<20.2f}\n",
                     f"{'Total Time (hours)':<30} {hr['total_time']:<20.2f} {br['total_time']:<20.2f}\n",
                     f"{'Execution Time (s)':<30} {ht:<20.6f} {bt:<20.6f}\n",
                     f"{'Speedup Factor':<30} {sp:<20.2f}x {'(baseline)':<20}\n","─"*70+"\n\n",
                     "COMPLEXITY ANALYSIS:\n","─"*70+"\n",
                     f"Heuristic: O(n²) time, O(n) space — handles 100+ spots | Actual: {ht:.6f}s\n",
                     f"Brute-Force: O(n!) time, O(n!) space — only feasible n<10 | Actual: {bt:.6f}s\n\n",
                     f"For n=5: Brute-force checks up to 120 permutations; Heuristic ~25 comparisons\n",
                     f"Speedup: {sp:.2f}x | Solution Quality: {acc:.1f}% of optimal\n\n",
                     "─"*70+"\nSCALABILITY PROJECTION:\n","─"*70+"\n",
                     f"{'n':<10}{'Brute-Force':<30}{'Heuristic':<25}\n","─"*70+"\n",
                     f"{'5':<10}{bt:<30.6f}{ht:<25.6f}\n",
                     f"{'10':<10}{'~years':<30}{'~0.001s est.':<25}\n",
                     f"{'20':<10}{'Intractable':<30}{'~0.004s est.':<25}\n",
                     f"{'50':<10}{'Intractable':<30}{'~0.025s est.':<25}\n"]
            self._write(self.cmp_txt, "".join(lines))
            messagebox.showinfo("Comparison Complete", f"Brute-force: {bt:.4f}s\nHeuristic: {ht:.4f}s\nSpeedup: {sp:.2f}x")
        except Exception as e: messagebox.showerror("Error", f"Comparison failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    TouristOptimizerGUI(root)
    root.mainloop()