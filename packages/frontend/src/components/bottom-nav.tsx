"use client"

import * as React from "react"
import {
    BarChart3,
    Bell,
    LayoutDashboard,
    Settings,
    TrendingUp,
} from "lucide-react"

const navItems = [
    {
        title: "Markets",
        url: "/markets",
        icon: TrendingUp,
    },
    {
        title: "Trade",
        url: "/trade",
        icon: LayoutDashboard,
    },
    {
        title: "Analytics",
        url: "/analytics",
        icon: BarChart3,
    },
    {
        title: "Alerts",
        url: "/alerts",
        icon: Bell,
    },
    {
        title: "Admin",
        url: "/admin",
        icon: Settings,
    },
]

export function BottomNav() {
    return (
        <nav className="fixed bottom-0 left-0 z-50 w-full h-16 bg-background border-t md:hidden">
            <div className="grid h-full max-w-lg grid-cols-5 mx-auto font-medium">
                {navItems.map((item) => (
                    <a
                        key={item.title}
                        href={item.url}
                        className="inline-flex flex-col items-center justify-center px-4 hover:bg-muted group"
                    >
                        <item.icon className="w-5 h-5 mb-1 text-muted-foreground group-hover:text-primary transition-colors" />
                        <span className="text-[10px] text-muted-foreground group-hover:text-primary transition-colors">
                            {item.title}
                        </span>
                    </a>
                ))}
            </div>
        </nav>
    )
}
