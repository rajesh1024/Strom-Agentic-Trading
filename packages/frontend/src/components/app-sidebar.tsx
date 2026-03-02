"use client"

import * as React from "react"
import {
    BarChart3,
    Bell,
    LayoutDashboard,
    Settings,
    TrendingUp,
} from "lucide-react"

import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarRail,
} from "@/components/ui/sidebar"

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

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
    return (
        <Sidebar collapsible="icon" {...props}>
            <SidebarHeader className="h-16 flex items-center justify-center border-b border-sidebar-border/50">
                <div className="flex items-center gap-2 px-4 w-full">
                    <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                        <TrendingUp className="size-4" />
                    </div>
                    <div className="flex flex-col gap-0.5 leading-none group-data-[collapsible=icon]:hidden">
                        <span className="font-semibold text-lg tracking-tight">STROM</span>
                        <span className="text-[10px] text-muted-foreground uppercase font-medium">Trading Agent</span>
                    </div>
                </div>
            </SidebarHeader>
            <SidebarContent>
                <SidebarMenu className="px-2 py-4">
                    {navItems.map((item) => (
                        <SidebarMenuItem key={item.title}>
                            <SidebarMenuButton asChild tooltip={item.title} className="h-10">
                                <a href={item.url} className="flex items-center gap-3">
                                    <item.icon className="size-5" />
                                    <span className="group-data-[collapsible=icon]:hidden">{item.title}</span>
                                </a>
                            </SidebarMenuButton>
                        </SidebarMenuItem>
                    ))}
                </SidebarMenu>
            </SidebarContent>
            <SidebarFooter className="border-t border-sidebar-border/50 p-4 group-data-[collapsible=icon]:hidden">
                <div className="flex flex-col gap-2">
                    <div className="flex items-center justify-between text-[11px] text-muted-foreground px-1">
                        <span>v1.0.0-alpha</span>
                        <span className="flex items-center gap-1">
                            <span className="size-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            Live
                        </span>
                    </div>
                </div>
            </SidebarFooter>
            <SidebarRail />
        </Sidebar>
    )
}
