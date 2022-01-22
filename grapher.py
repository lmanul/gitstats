"Draws visual graphs from statistics"

import os
import sys

def draw_weeks(weeks, output_file):
    "Draws a weekly stats graph"
    weeks_out = []
    for week in weeks:
        weeks_out.append(week + ":" + ":".join([str(a) for a in weeks[week]]))

    chart_js = open(os.path.join(sys.path[0], "helpers/Chart.bundle.min.js")).read()
    template = open(os.path.join(sys.path[0], "template.html")).read()
    output = template
    output = output.replace("{{CHART_JS}}", chart_js)
    output = output.replace("{{WEEKS}}", "|".join(weeks_out))

    f = open(output_file, "w")
    f.write(output)
    f.close()
