"use client"

import * as React from "react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

export type Status = "success" | "warning" | "error" | "info" | "pending" | "critical"

export interface StatusBadgeProps {
    status: Status | string
    label?: string
    className?: string
    dot?: boolean
}

const statusStyles: Record<string, { bg: string, text: string, dot: string }> = {
    success: { bg: "bg-emerald-500/10", text: "text-emerald-500", dot: "bg-emerald-500" },
    warning: { bg: "bg-amber-500/10", text: "text-amber-500", dot: "bg-amber-500" },
    error: { bg: "bg-red-500/10", text: "text-red-500", dot: "bg-red-500" },
    critical: { bg: "bg-destructive/10", text: "text-destructive", dot: "bg-destructive" },
    info: { bg: "bg-blue-500/10", text: "text-blue-500", dot: "bg-blue-500" },
    pending: { bg: "bg-slate-500/10", text: "text-slate-500", dot: "bg-slate-500" },
}

export function StatusBadge({ status, label, className, dot = true }: StatusBadgeProps) {
    const normalizedStatus = status.toLowerCase() as Status
    const style = statusStyles[normalizedStatus] || statusStyles.pending

    return (
        <Badge
            variant="outline"
            className={cn(
                "flex items-center gap-1.5 px-2 py-0.5 font-medium border-transparent",
                style.bg,
                style.text,
                className
            )}
            aria-label={`Status: ${label || status}`}
        >
            {dot && <span data-testid="status-dot" className={cn("size-1.5 rounded-full transition-all animate-pulse", style.dot)} />}
            <span className="capitalize">{label || status}</span>
        </Badge>
    )
}
