"use client"

import * as React from "react"
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { TopBar } from "@/components/top-bar"
import { BottomNav } from "@/components/bottom-nav"

export function LayoutShell({ children }: { children: React.ReactNode }) {
    return (
        <SidebarProvider>
            <div className="flex min-h-screen w-full bg-background overflow-hidden">
                <AppSidebar />
                <SidebarInset className="flex flex-col flex-1 overflow-hidden">
                    <TopBar />
                    <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-20 md:pb-6">
                        <div className="max-w-7xl mx-auto w-full">
                            {children}
                        </div>
                    </main>
                </SidebarInset>
                <BottomNav />
            </div>
        </SidebarProvider>
    )
}
