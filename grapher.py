"Draws visual graphs from statistics"

import os
import sys

def draw_weeks_and_quarters(weeks, quarters, output_file):
    "Draws a weekly and a quarterly stats graph"
    weeks_out = []
    quarters_out = []
    for week in weeks:
        weeks_out.append(week + ":" + ":".join([str(a) for a in weeks[week]]))
    for quarter in quarters:
        quarters_out.append(quarter + ":" + ":".join([str(a) for a in quarters[quarter]]))

    chart_js = open(os.path.join(sys.path[0], "helpers/Chart.bundle.min.js")).read()
    template = open(os.path.join(sys.path[0], "template.html")).read()
    output = template
    output = output.replace("{{CHART_JS}}", chart_js)
    output = output.replace("{{WEEKS}}", "|".join(weeks_out))
    output = output.replace("{{QUARTERS}}", "|".join(quarters_out))

    f = open(output_file, "w")
    f.write(output)
    f.close()

