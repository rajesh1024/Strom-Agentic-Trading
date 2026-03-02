import { LayoutShell } from "@/components/layout-shell"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Activity } from "lucide-react"
import { MetricCard } from "@/components/shared/metric-card"
import { StatusBadge } from "@/components/shared/status-badge"

export default function Home() {
  return (
    <LayoutShell>
      <div className="space-y-6 animate-in fade-in duration-500">
        <header className="flex flex-col gap-1">
          <h1 className="text-3xl font-bold tracking-tight">Market Overview</h1>
          <p className="text-muted-foreground">Real-time market activity and trading signals.</p>
        </header>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <MetricCard title="Total Volume" value="$4.2B" change="+12.5%" trend="up" description="from last session" />
          <MetricCard title="Active Trades" value="12" change="+2" trend="up" description="running now" />
          <MetricCard title="System Performance" value="99.9%" change="-0.02%" trend="down" description="latency spike" />
          <MetricCard title="Risk Level" value="Low" change="Stable" trend="neutral" description="within limits" />
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
          <Card className="lg:col-span-4 bg-card/50 backdrop-blur">
            <CardHeader>
              <CardTitle>Trade Execution Analytics</CardTitle>
              <CardDescription>Live feed of system advisory signals and executions.</CardDescription>
            </CardHeader>
            <CardContent className="h-[300px] flex items-center justify-center border-t border-dashed">
              <div className="flex flex-col items-center gap-2 text-muted-foreground">
                <Activity className="size-8 animate-pulse" />
                <p className="text-sm font-medium">Waiting for market data...</p>
              </div>
            </CardContent>
          </Card>

          <Card className="lg:col-span-3 bg-card/50 backdrop-blur">
            <CardHeader>
              <CardTitle>Recent Alerts</CardTitle>
              <CardDescription>Critical system and market notifications.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { msg: "BTC/USDT Breakout detected", time: "2m ago", status: "success", label: "advisory" },
                  { msg: "Margin level alert: 85%", time: "15m ago", status: "warning", label: "warning" },
                  { msg: "Order filled: 1.2 ETH @ $2,450", time: "44m ago", status: "info", label: "system" },
                ].map((alert, i) => (
                  <div key={i} className="flex items-center justify-between text-sm">
                    <div className="flex flex-col">
                      <span className="font-medium">{alert.msg}</span>
                      <span className="text-[11px] text-muted-foreground">{alert.time}</span>
                    </div>
                    <StatusBadge status={alert.status as any} label={alert.label} className="h-5 text-[10px]" />
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </LayoutShell>
  )
}
