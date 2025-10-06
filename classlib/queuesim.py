
from __future__ import annotations
from dataclasses import dataclass
import math
import numpy as np
import matplotlib.pyplot as plt

GLOBAL_RNG = np.random.default_rng()

@dataclass
class BaseCfg:
    t_end: float | None = 2000.0
    n_complete: int | None = None
    record_state_trajectory: bool = True

class BaseSim:
    def __init__(self, cfg: BaseCfg, rng: np.random.Generator | None = None):
        self.cfg = cfg
        self.rng = GLOBAL_RNG if rng is None else rng
        self.t = 0.0
        self._areas_n = 0.0
        self._last_t = 0.0
        self.state_t = []
        self.state_n = []

    def n_system(self) -> int:
        return 0

    def _init_traj(self):
        if self.cfg.record_state_trajectory:
            self.state_t = [0.0]
            self.state_n = [self.n_system()]
        else:
            self.state_t = []
            self.state_n = []

    def _update_area(self, new_t: float):
        dt = new_t - self._last_t
        if dt > 0:
            self._areas_n += self.n_system() * dt
            self._last_t = new_t

    def _record_state(self):
        if self.cfg.record_state_trajectory:
            self.state_t.append(self.t)
            self.state_n.append(self.n_system())

    def sim_time(self) -> float:
        return self.t if self.cfg.t_end is None else min(self.t, self.cfg.t_end)

def step_plot(sim: BaseSim, title: str = "System Size Over Time") -> None:
    if sim.cfg.record_state_trajectory and sim.state_t:
        plt.figure(figsize=(8,4))
        plt.step(sim.state_t, sim.state_n, where="post")
        plt.xlabel("time, $t$")
        plt.ylabel("$N(t)$ in system")
        plt.title(title)
        plt.show()

@dataclass
class A_Config(BaseCfg):
    lambda_: float = 0.8
    service_a: float = 0.8
    service_b: float = 1.2

class SingleServerEU1(BaseSim):
    def __init__(self, cfg: A_Config, rng: np.random.Generator | None = None):
        super().__init__(cfg, rng)
        self.cfg: A_Config
        self.queue: list[int] = []
        self.server_cid: int | None = None
        self.customers: list[dict] = []
        self.next_id = 0
        self.sum_service = 0.0
        self.t_arr = self.t + self.rng.exponential(1.0/self.cfg.lambda_)
        self.t_dep = math.inf
        self._init_traj()

    def n_system(self) -> int:
        return len(self.queue) + (1 if self.server_cid is not None else 0)

    def _srv(self) -> float:
        return self.rng.uniform(self.cfg.service_a, self.cfg.service_b)

    def _arrival(self) -> None:
        cid = self.next_id; self.next_id += 1
        self.customers.append({"id": cid, "a": self.t, "s": None, "d": None, "srv": None})
        if self.server_cid is None:
            self.server_cid = cid
            s = self._srv()
            self.customers[cid]["s"] = self.t
            self.customers[cid]["srv"] = s
            self.sum_service += s
            self.t_dep = self.t + s
        else:
            self.queue.append(cid)
        self.t_arr = self.t + self.rng.exponential(1.0/self.cfg.lambda_)

    def _depart(self) -> None:
        cid = self.server_cid
        self.customers[cid]["d"] = self.t
        if self.queue:
            next_id = self.queue.pop(0)
            self.server_cid = next_id
            s = self._srv()
            self.customers[next_id]["s"] = self.t
            self.customers[next_id]["srv"] = s
            self.sum_service += s
            self.t_dep = self.t + s
        else:
            self.server_cid = None
            self.t_dep = math.inf

    def run(self) -> None:
        target_t = self.cfg.t_end if self.cfg.t_end is not None else math.inf
        target_n = self.cfg.n_complete if self.cfg.n_complete is not None else math.inf
        while (self.t < target_t) and (self._n_departed() < target_n):
            t_next = min(self.t_arr, self.t_dep)
            self._update_area(t_next); self.t = t_next
            if abs(self.t - self.t_dep) < 1e-12:
                self._depart()
            else:
                self._arrival()
            self._record_state()
        self._update_area(min(self.t, target_t))

    def _n_departed(self) -> int:
        return sum(1 for c in self.customers if c["d"] is not None)

    def summary(self) -> dict:
        simT = self.sim_time()
        served = [c for c in self.customers if c["d"] is not None]
        if not served:
            return {"sim_time": simT, "departures": 0}
        waits = [c["s"] - c["a"] for c in served]
        totals = [c["d"] - c["a"] for c in served]
        lam_hat = len(self.customers)/simT if simT>0 else np.nan
        return {
            "sim_time": simT,
            "arrivals": len(self.customers),
            "departures": len(served),
            "lambda_hat": lam_hat,
            "avg_L": self._areas_n/simT if simT>0 else np.nan,
            "avg_Wq": float(np.mean(waits)),
            "avg_W": float(np.mean(totals)),
            "L_via_Little": lam_hat*float(np.mean(totals)) if simT>0 else np.nan,
            "util_est": self.sum_service/simT if simT>0 else np.nan,
            "mean_service": self.sum_service/max(1,len(served)),
        }

@dataclass
class B_Config(BaseCfg):
    lambda_: float = 0.9
    s1_a: float = 0.7; s1_b: float = 1.1
    s2_a: float = 0.5; s2_b: float = 1.0
    K2_total: int = 6

class DriveThruBlocking(BaseSim):
    def __init__(self, cfg: B_Config, rng: np.random.Generator | None = None):
        super().__init__(cfg, rng)
        self.cfg: B_Config
        self.customers: list[dict] = []
        self.next_id = 0
        self.q1: list[int] = []; self.q2: list[int] = []
        self.s1_cid: int | None = None; self.s2_cid: int | None = None
        self.s1_blocked: bool = False; self.blocked_cid: int | None = None
        self.block_time = 0.0
        self.s1_service_sum = 0.0; self.s2_service_sum = 0.0
        self.t_arr = self.t + self.rng.exponential(1.0/self.cfg.lambda_)
        self.t_s1_dep = math.inf; self.t_s2_dep = math.inf
        self._init_traj()

    def n_stage2_total(self) -> int: 
        return len(self.q2) + (1 if self.s2_cid is not None else 0)
    def n_system(self) -> int:
        return len(self.q1)+len(self.q2)+(1 if self.s1_cid is not None else 0)+(1 if self.s2_cid is not None else 0)+(1 if self.s1_blocked else 0)

    def _update_area(self, new_t: float):
        dt = new_t - self._last_t
        if dt > 0:
            self._areas_n += self.n_system() * dt
            if self.s1_blocked: self.block_time += dt
            self._last_t = new_t

    def _s1(self) -> float: return self.rng.uniform(self.cfg.s1_a, self.cfg.s1_b)
    def _s2(self) -> float: return self.rng.uniform(self.cfg.s2_a, self.cfg.s2_b)

    def _arrival(self) -> None:
        cid = self.next_id; self.next_id += 1
        self.customers.append({"id": cid, "a": self.t, "s1s": None, "s1d": None, "s1srv": None, "s2s": None, "d": None, "s2srv": None})
        if (self.s1_cid is None) and (not self.s1_blocked):
            self.s1_cid = cid
            s = self._s1()
            self.customers[cid]["s1s"] = self.t
            self.customers[cid]["s1srv"] = s
            self.s1_service_sum += s
            self.t_s1_dep = self.t + s
        else:
            self.q1.append(cid)
        self.t_arr = self.t + self.rng.exponential(1.0/self.cfg.lambda_)

    def _s1_depart(self) -> None:
        cid = self.s1_cid
        self.customers[cid]["s1d"] = self.t
        if self.n_stage2_total() >= self.cfg.K2_total:
            self.s1_blocked = True; self.blocked_cid = cid
            self.s1_cid = None; self.t_s1_dep = math.inf
            return
        if self.s2_cid is None:
            self.s2_cid = cid
            s2 = self._s2()
            self.customers[cid]["s2s"] = self.t
            self.customers[cid]["s2srv"] = s2
            self.s2_service_sum += s2
            self.t_s2_dep = self.t + s2
        else:
            self.q2.append(cid)
        if self.q1:
            nid = self.q1.pop(0)
            self.s1_cid = nid
            s1 = self._s1()
            self.customers[nid]["s1s"] = self.t
            self.customers[nid]["s1srv"] = s1
            self.s1_service_sum += s1
            self.t_s1_dep = self.t + s1
        else:
            self.s1_cid = None; self.t_s1_dep = math.inf

    def _s2_depart(self) -> None:
        cid = self.s2_cid
        self.customers[cid]["d"] = self.t
        if self.q2:
            nid = self.q2.pop(0)
            self.s2_cid = nid
            s2 = self._s2()
            self.customers[nid]["s2s"] = self.t
            self.customers[nid]["s2srv"] = s2
            self.s2_service_sum += s2
            self.t_s2_dep = self.t + s2
        else:
            self.s2_cid = None; self.t_s2_dep = math.inf
        if self.s1_blocked and (self.n_stage2_total() < self.cfg.K2_total):
            cidb = self.blocked_cid
            self.s1_blocked = False; self.blocked_cid = None
            if self.s2_cid is None:
                self.s2_cid = cidb
                s2 = self._s2()
                self.customers[cidb]["s2s"] = self.t
                self.customers[cidb]["s2srv"] = s2
                self.s2_service_sum += s2
                self.t_s2_dep = self.t + s2
            else:
                self.q2.append(cidb)
            if (self.s1_cid is None) and self.q1:
                nid = self.q1.pop(0)
                self.s1_cid = nid
                s1 = self._s1()
                self.customers[nid]["s1s"] = self.t
                self.customers[nid]["s1srv"] = s1
                self.s1_service_sum += s1
                self.t_s1_dep = self.t + s1

    def _departed_count(self) -> int:
        return sum(1 for c in self.customers if c["d"] is not None)

    def run(self) -> None:
        target_t = self.cfg.t_end if self.cfg.t_end is not None else math.inf
        target_n = self.cfg.n_complete if self.cfg.n_complete is not None else math.inf
        while (self.t < target_t) and (self._departed_count() < target_n):
            t_next = min(self.t_arr, self.t_s1_dep, self.t_s2_dep)
            self._update_area(t_next); self.t = t_next
            if abs(self.t - self.t_s2_dep) < 1e-12:
                self._s2_depart()
            elif abs(self.t - self.t_s1_dep) < 1e-12:
                self._s1_depart()
            else:
                self._arrival()
            self._record_state()
        self._update_area(min(self.t, target_t))

    def summary(self) -> dict:
        simT = self.sim_time()
        served = [c for c in self.customers if c["d"] is not None]
        if not served:
            return {"sim_time": simT, "departures": 0}
        s1w = [c["s1s"] - c["a"] for c in served]
        s2w = [c["s2s"] - c["s1d"] for c in served]
        tot = [c["d"] - c["a"] for c in served]
        return {
            "sim_time": simT,
            "arrivals": len(self.customers),
            "departures": len(served),
            "avg_N": self._areas_n/simT if simT>0 else np.nan,
            "avg_s1_wait": float(np.mean(s1w)),
            "avg_s2_wait": float(np.mean(s2w)),
            "avg_total_time": float(np.mean(tot)),
            "s1_util_est": self.s1_service_sum/simT if simT>0 else np.nan,
            "s2_util_est": self.s2_service_sum/simT if simT>0 else np.nan,
            "blocking_fraction_time": getattr(self, "block_time", 0.0)/simT if simT>0 else 0.0,
            "K2_total": self.cfg.K2_total,
            "lambda_param": self.cfg.lambda_,
        }
