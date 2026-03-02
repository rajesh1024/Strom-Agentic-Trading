"use client"

import * as React from "react"
import { Power, Activity, ShieldCheck } from "lucide-react"
import { ModeToggle } from "@/components/mode-toggle"
import { Button } from "@/components/ui/button"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Badge } from "@/components/ui/badge"
import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
} from "@/components/ui/tooltip"

export function TopBar() {
    const [mode, setMode] = React.useState<"advisory" | "semi-auto">("advisory")
    const [isConnected] = React.useState(true)

    return (
        <header className="sticky top-0 z-30 flex h-16 w-full shrink-0 items-center justify-between border-b bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex items-center gap-4">
                <SidebarTrigger className="-ml-1 h-9 w-9" />
                <div className="h-6 w-px bg-border hidden sm:block" />
                <div className="flex items-center gap-2">
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className="flex items-center gap-2 px-2 py-1 rounded-md hover:bg-accent/50 transition-colors cursor-help">
                                <div className={`size-2.5 rounded-full ${isConnected ? "bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" : "bg-red-500"}`} />
                                <span className="text-sm font-medium hidden sm:inline-block">Connected</span>
                            </div>
                        </TooltipTrigger>
                        <TooltipContent>
                            <p>Trading Engine: WebSocket Active</p>
                        </TooltipContent>
                    </Tooltip>
                </div>
            </div>

            <div className="flex items-center gap-3">
                <div className="hidden lg:flex items-center gap-2 mr-4 bg-muted/50 px-3 py-1.5 rounded-full border border-border/50">
                    <Activity className="size-4 text-primary" />
                    <span className="text-[13px] font-medium">Session: 04:22:15</span>
                </div>

                <div className="flex items-center gap-2">
                    <Badge
                        variant={mode === "semi-auto" ? "destructive" : "secondary"}
                        className="h-8 px-3 cursor-pointer hover:opacity-80 transition-all gap-1.5 flex items-center"
                        onClick={() => setMode(mode === "advisory" ? "semi-auto" : "advisory")}
                    >
                        {mode === "semi-auto" ? (
                            <ShieldCheck className="size-3.5" />
                        ) : (
                            <Activity className="size-3.5" />
                        )}
                        <span className="uppercase tracking-wider text-[10px] font-bold">
                            {mode === "advisory" ? "Advisory" : "Semi-Auto"}
                        </span>
                    </Badge>
                </div>

                <div className="h-4 w-px bg-border mx-1" />

                <Button
                    variant="destructive"
                    size="sm"
                    className="h-9 px-4 font-bold tracking-tight uppercase shadow-lg shadow-destructive/20 hover:shadow-destructive/40 transition-all gap-2"
                >
                    <Power className="size-4" />
                    <span className="hidden sm:inline">Kill Switch</span>
                </Button>

                <ModeToggle />
            </div>
        </header>
    )
}
