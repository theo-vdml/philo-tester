from textual import work, on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Label, Static, Collapsible, Log, Button, TabbedContent, DataTable, ProgressBar
from textual.events import Click
from typing import Callable, List, Dict
import re

TestCase = Dict
TestCaseList = List[TestCase]
CheckerFunction = Callable[[TestCase, str, Dict], bool]

log_regex = "^([0-9]+)\s([0-9]+)\s\s(is thinking|is sleeping|has taken a fork|is eating|died)$"

def checker_no_die(test_case: TestCase, logs: List[str], data: Dict) -> Dict:

    for line in logs:
        ## Check that line match with philosophers logs
        _match = re.search(log_regex, line)
        if (_match == None):
            return { "result": False, "message": f"Logs does not match the required log format :\n {line}" }
    
    # Split args into an array [count, t2d, t2e, t2s, max]
    args = test_case["args"].split(" ")
    count = int(args[0])
    t2d = int(args[1])
    t2e = int(args[2])
    t2s = int(args[3])

    philo_count = len(data.keys())

    # Check that summary len (number of philo in simulation) match args requirment (count)
    if (philo_count is not count):
        return { "result": False, "message": f"Wainting {count} philos, {philo_count} found." }
    
    # Check data summary of all philos 
    for id, philo in data.items():

        # explode vars 
        eat = philo["eat"]
        sleep = philo["sleep"]
        died = philo["died"]
        short_sleep = philo["short_sleep"]
        short_eat = philo["short_eat"]
        max_time_no_eat = philo["max_time_no_eat"]

        # Return an error if any philosopher died
        if (died):
            return { "result": False, "message": f"Philo {id} died" }
        
        # Return an error if any philosopher should have died and you didn't returned it 
        if (max_time_no_eat >= t2d):
            return { "result": False, "message": f"Philo {id} asn't eat for {max_time_no_eat}ms and he dind't died."}

        # Return an error if any philosopher forgot to sleep (allow one sleep less than eating because could end before sleeping)
        if (eat - sleep > 1):
            return { "result": False, "message": f"Philosopher {id} forgot to sleep after eating" }
        
        # Return an error if any philosopher had a too short sleep
        if (short_sleep < t2s):
            return { "result": False, "message": f"Philo {id} slept {short_sleep}ms but time to sleep is longer: {t2s}." }
        
        # Return an error if any philosopher had a too short eat
        if (short_eat < t2e):
            return { "result": False, "message": f"Philo {id} ate {short_sleep}ms but time to eat is longer: {t2s}." }

    return { "result": True, "message": "" }

def checker_no_die_limit(test_case: TestCase, logs: str, data: Dict) -> Dict:

    for line in logs:
        ## Check that line match with philosophers logs
        _match = re.search(log_regex, line)
        if (_match == None):
            return { "result": False, "message": f"Logs does not match the required log format :\n {line}" }
    
    # Split args into an array [count, t2d, t2e, t2s, max]
    args = test_case["args"].split(" ")
    count = int(args[0])
    t2d = int(args[1])
    t2e = int(args[2])
    t2s = int(args[3])
    limit = int(args[4])

    philo_count = len(data.keys())

    # Check that summary len (number of philo in simulation) match args requirment (count)
    if (philo_count is not count):
        return { "result": False, "message": f"Wainting {count} philos, {philo_count} found." }
    
    min_ate = -1

    # Check data summary of all philos 
    for id, philo in data.items():

        # explode vars 
        eat = philo["eat"]
        sleep = philo["sleep"]
        died = philo["died"]
        short_sleep = philo["short_sleep"]
        short_eat = philo["short_eat"]
        max_time_no_eat = philo["max_time_no_eat"]

        # Return an error if any philosopher died
        if (died):
            return { "result": False, "message": f"Philo {id} died" }
        
        # Return an error if any philosopher should have died and you didn't returned it 
        if (max_time_no_eat >= t2d):
            return { "result": False, "message": f"Philo {id} asn't eat for {max_time_no_eat}ms and he dind't died."}

        # Return an error if any philosopher forgot to sleep (allow one sleep less than eating because could end before sleeping)
        if (eat - sleep > 1):
            return { "result": False, "message": f"Philosopher {id} forgot to sleep after eating" }
        
        # Return an error if any philosopher had a too short sleep
        if (short_sleep < t2s):
            return { "result": False, "message": f"Philo {id} slept {short_sleep}ms but time to sleep is longer: {t2s}." }
        
        # Return an error if any philosopher had a too short eat
        if (short_eat < t2e):
            return { "result": False, "message": f"Philo {id} ate {short_sleep}ms but time to eat is longer: {t2s}." }
        
        if (eat < limit):
            return { "result": False, "message": f"Philo {id} ate {eat} times but requirment was eating {limit} times." }
        
        if (min_ate == -1):
            min_ate = eat
        min_ate = min(min_ate, eat)

    if (min_ate is not limit):
        return { "result": False, "message": f"Philosophers have eat too many times, limit was {limit} but everyone ate at least {min_ate} times" }


    return { "result": True, "message": "" }


def checker_die(test_case: TestCase, logs: List[str], data: Dict) -> Dict:

    for line in logs:
        ## Check that line match with philosophers logs
        _match = re.search(log_regex, line)
        if (_match == None):
            return { "result": False, "message": f"Logs does not match the required log format :\n {line}" }
    
    # Split args into an array [count, t2d, t2e, t2s, max]
    args = test_case["args"].split(" ")
    t2d = int(args[1])
    t2e = int(args[2])
    t2s = int(args[3])

    died_total = 0
    
    # Check data summary of all philos 
    for id, philo in data.items():

        # explode vars 
        eat = philo["eat"]
        sleep = philo["sleep"]
        died = philo["died"]
        short_sleep = philo["short_sleep"]
        short_eat = philo["short_eat"]
        max_time_no_eat = philo["max_time_no_eat"]
        time_to_die = philo["time_to_die"]

        # Return an error if any philosopher died
        died_total += died

        if (died):
            if (time_to_die > t2d + 10):
                return { "result": False, "message": f"Philo {id} death happend {time_to_die}ms after the last meal, time to die was {t2d} and a delay of more than 10ms is not accepted."}

        # Return an error if any philosopher should have died and you didn't returned it 
        if (max_time_no_eat >= t2d):
            return { "result": False, "message": f"Philo {id} asn't eat for {max_time_no_eat}ms and he dind't died."}

        # Return an error if any philosopher forgot to sleep (allow one sleep less than eating because could end before sleeping)
        if (eat - sleep > 1):
            return { "result": False, "message": f"Philosopher {id} forgot to sleep after eating" }
        
        # Return an error if any philosopher had a too short sleep
        if (short_sleep < t2s):
            return { "result": False, "message": f"Philo {id} slept {short_sleep}ms but time to sleep is longer: {t2s}." }
        
        # Return an error if any philosopher had a too short eat
        if (short_eat < t2e):
            return { "result": False, "message": f"Philo {id} ate {short_sleep}ms but time to eat is longer: {t2s}." }

    return { "result": True, "message": "" }

classic_tests: TestCaseList = [
    {"args": "4 410 200 200", "checker": checker_no_die, "timeout": 30, "behavior": "No philosophers should die."},
    {"args": "5 600 150 150", "checker": checker_no_die, "timeout": 30, "behavior": "No philosophers should die."},
    {"args": "5 800 200 200", "checker": checker_no_die, "timeout": 30, "behavior": "No philosophers should die."},
    {"args": "100 800 200 200", "checker": checker_no_die, "timeout": 30, "behavior": "No philosophers should die."},
    {"args": "105 800 200 200", "checker": checker_no_die, "timeout": 30, "behavior": "No philosophers should die."},
    {"args": "200 800 200 200", "checker": checker_no_die, "timeout": 30, "behavior": "No philosophers should die."},
    {"args": "4 410 200 200 7", "checker": checker_no_die_limit, "timeout": -1, "behavior": "All philosophers should have eat at least 7 times.\nNo philosophers should die."},
    {"args": "4 410 200 200 15", "checker": checker_no_die_limit, "timeout": -1, "behavior": "All philosophers should have eat at least 15 times.\nNo philosophers should die."}
]

death_tests: TestCaseList = [
    {"args": "1 410 200 200", "checker": checker_die, "timeout": 30, "behavior": "The philosopher should not eat and die."},
    {"args": "4 310 200 100", "checker": checker_die, "timeout": 30, "behavior": "The philosopher should not eat and die."},
    {"args": "4 200 205 200", "checker": checker_die, "timeout": 30, "behavior": "The philosopher should not eat and die."},
    {"args": "5 410 200 200", "checker": checker_die, "timeout": 30, "behavior": "A philosophers should die and the program should stop."}
]

error_tests: TestCaseList = [
    {"args": "4 410 -200 200", "checker": None, "timeout": 3, "behavior": "Program should not accept negative number.\nCrash are not acceptables"},
    {"args": "5 800 aba 200", "checker": None, "timeout": 30, "behavior": "Program should not accept non integer values.\nCrash are not acceptables"},
    {"args": "5 800 200", "checker": None, "timeout": 30, "behavior": "Program should return an error for missing argument"},
]

class TestCaseBlock(Static):

    # Init the test case
    def __init__(self, test_case: TestCase, index: int, **kwargs):
        super().__init__(**kwargs)
        self.test_case = test_case
        self.args = test_case["args"]
        self.command = "./philo"
        self.command_args = self.args.split(" ")
        self.index = str(index)
        self.checker: CheckerFunction = test_case["checker"]
        self.timeout = test_case["timeout"]
        self.behavior = test_case["behavior"]

    # Woker that handle the subprosses to run the test case
    @work(exclusive=True, thread=True)
    async def run_command(self):
        """Run the command in a background thread using a worker."""
        import subprocess
        import time

        command = ["stdbuf", "-oL", self.command] + self.command_args
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        start_time = time.time()
        timeout = self.timeout  # Timeout in seconds

        try:
            output = []
            output_lines = []
            while True:
                line = process.stdout.readline()
                if line:
                    output_lines.append(line)
                    output.append(line)

                current_time = time.time()
                elapsed_time = current_time - start_time
                    
                # Update log every 10 lines
                if len(output_lines) >= 10:
                    self.app.call_from_thread(self.update_log, "".join(output_lines), elapsed_time)
                    self.app.call_from_thread(self.get_summary, output)
                    output_lines.clear()

                if elapsed_time > timeout and timeout > -1:
                    process.kill()
                    break

                if process.poll() is not None:
                    break

            # Update any remaining lines in the log
            if output_lines:
                self.app.call_from_thread(self.update_log, "".join(output_lines), elapsed_time)

        except Exception as e:
            self.app.call_from_thread(self.update_log, f"Error: {str(e)}\n", self.timeout)
        finally:
            process.stdout.close()
            process.wait()
            self.app.call_from_thread(self.get_summary, output)
            self.app.call_from_thread(self.call_checker, output)

    # Function that return a data object from the logs string
    def get_data(self, logs: list[str]):
        ## Init data as an empty object
        data = {}
        ## Set a default philosopher object
        default_philo = {
            # Actions count
            "eat": 0, 
            "sleep": 0, 
            "think": 0, 
            "fork": 0, 
            "died": 0, 
            # No eating
            "last_meal": 0, 
            "max_time_no_eat": 0, 
            "time_to_die": 0,
            # Action durations
            "long_sleep": 0,
            "short_sleep": 999999999999999999999,
            "long_eat": 0,
            "short_eat": 999999999999999999999,
            # Last action data
            "last_action": "",
            "last_action_time": 0
        }
        for line in logs:
            ## Check that line match with philosophers logs
            _match = re.search(log_regex, line)
            if (_match != None):

                ## Get time, philo id, and action from regex groups
                time = int(_match.group(1))
                philo = int(_match.group(2))
                action = _match.group(3)

                ## Rename actions with keywords
                if (action == "is thinking"): action = "think"
                if (action == "is sleeping"): action = "sleep"
                if (action == "has taken a fork"): action = "fork"
                if (action == "is eating"): action = "eat"

                ## Add philosopher to data if not already in
                if (philo not in data):
                    data[philo] = default_philo.copy()

                ## Register shortest and longest time to perform an action
                if data[philo]["last_action"] in ["eat", "sleep"]:
                    data[philo][f"short_{data[philo]['last_action']}"] = min(time - data[philo]["last_action_time"], data[philo][f"short_{data[philo]['last_action']}"])
                    data[philo][f"long_{data[philo]['last_action']}"] = max(time - data[philo]["last_action_time"], data[philo][f"long_{data[philo]['last_action']}"])

                ## Keep count of each time a philosopher did an action
                data[philo][action] += 1
                data[philo]["last_action"] = action
                data[philo]["last_action_time"] = time                    
                
                ## Get the maximum time spend without eating
                if (action == "eat"):
                    data[philo]["max_time_no_eat"] = max(int(time) - data[philo]["last_meal"], data[philo]["max_time_no_eat"])
                    data[philo]["last_meal"] = int(time)

                ## Get the time between last meal and death record
                if (action == "died"):
                    data[philo]["time_to_die"] = int(time) - data[philo]["last_meal"]

        return data

    # Function that upadate the database summary
    def get_summary(self, logs: list[str]):
        datatable: DataTable = self.query_one("DataTable")
        datatable.clear(columns=True)
        philosophers = self.get_data(logs)  
        summary = [("Philo", "Eat", "Sleep", "Think", "Forks")]
        for id, data in philosophers.items():
            summary.append((id, data["eat"], data["sleep"], data["think"], data["fork"]))

        datatable.add_columns(*summary[0])
        datatable.add_rows(summary[1:])
        datatable.cursor_type = "none"
        datatable.zebra_stripes = True

    # Fucntion that call the revelent checker function for the test case
    def call_checker(self, logs: str):
        data = self.get_data(logs)
        checker_el: Label = self.query_one(".checker-result")
        title_el = self.query_one("CollapsibleTitle")
        if (self.checker):
            result: Dict = self.checker(self.test_case, logs, data)
            if (result["result"]):
                checker_el.update("Success")
                checker_el.add_class("success")
                title_el.add_class("success")
            else:
                checker_el.update("[Failed] " + result["message"])
                checker_el.add_class("fail")
                title_el.add_class("fail")
        else:
            checker_el.update("You should check by yourself")
            checker_el.add_class("pending")
            title_el.add_class("pending")

    # Function that update the log element while subprocess is runing
    def update_log(self, log_content: str, progress: int = None):
        log_el: Log = self.query_one(Log)
        log_el.write(log_content)  # Update log with the batch of lines
        if (self.timeout > -1):
            if (progress):
                progress_bar: ProgressBar = self.query_one("ProgressBar")
                progress_bar.progress = progress

    # The component render function
    def compose(self) -> ComposeResult:
        with Collapsible(classes="collapsible", title=self.index + ') ' + self.command + ' ' + ' '.join(self.command_args), collapsed=True, collapsed_symbol="▷ ", expanded_symbol="▽ "):
            yield Button("▶ Start test", variant="primary", classes="buttons")
            yield Label("Expected behavior :", classes="behavior-title")
            yield Label(self.behavior, classes="behavior")
            if (self.timeout > -1):
                yield Label("Auto timeout :", classes="timeout-title")
                yield Label("After " + str(self.timeout) + " seconds", classes="timeout")
            yield Label("Checker Result :", classes="checker-title")
            yield Label("Waiting for unit test to start ...", classes="checker-result")
            if (self.timeout > -1):
                yield ProgressBar(show_eta=False, total=self.timeout)
            with TabbedContent("Logs", "Summary"):
                yield Log(classes="log")
                yield DataTable()

    # Handle the start button pressed
    def on_button_pressed(self, event: Button.Pressed) -> None:
        log_el: Log = self.query_one(Log)
        log_el.clear()
        self.run_command()  # Run the command in the background
        checker_el: Label = self.query_one(".checker-result")
        title_el = self.query_one("CollapsibleTitle")
        checker_el.update("Pending ...")
        title_el.remove_class("pending")
        checker_el.remove_class("pending")
        title_el.remove_class("success")
        checker_el.remove_class("success")
        title_el.remove_class("fail")
        checker_el.remove_class("fail")


class TestCaseGroup(Static):
    def __init__(self, test_cases: TestCaseList, **kwargs):
        super().__init__(**kwargs)
        self.test_cases = test_cases
    
    def compose(self) -> ComposeResult:
        for index, test_case in enumerate(self.test_cases):
            yield TestCaseBlock(test_case=test_case, index=index)
        

class MyFooter(Footer):
    def compose(self) -> ComposeResult:
        yield Label("@theo_vdml - Made for school 42", id="footer-label")

class PhiloTester(App):

    CSS_PATH = "styles.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield MyFooter(show_command_palette=False, id="footer")
        with TabbedContent("Classic Tests", "Death Test", "Errors Test"):
            yield TestCaseGroup(classic_tests)
            yield TestCaseGroup(death_tests)
            yield TestCaseGroup(error_tests)
            

if __name__ == "__main__":
    app = PhiloTester()
    app.run()
