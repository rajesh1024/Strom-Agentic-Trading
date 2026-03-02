"use client"

import * as React from "react"
import { ArrowDownRight, ArrowUpRight, TrendingUp } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

export interface MetricCardProps {
    title: string
    value: string | number
    change?: string
    trend?: "up" | "down" | "neutral"
    icon?: React.ReactNode
    description?: string
    className?: string
}

export function MetricCard({
    title,
    value,
    change,
    trend = "neutral",
    icon,
    description,
    className,
}: MetricCardProps) {
    return (
        <Card className={cn("overflow-hidden border-border/50 bg-card/30 backdrop-blur transition-all hover:bg-card/40", className)}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
                <div className="p-2 bg-primary/10 rounded-full">
                    {icon || <TrendingUp className="size-4 text-primary" />}
                </div>
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold tracking-tight">{value}</div>
                <div className="flex items-center gap-1.5 mt-1">
                    {trend === "up" && <ArrowUpRight className="size-3.5 text-emerald-500" />}
                    {trend === "down" && <ArrowDownRight className="size-3.5 text-red-500" />}
                    {change && (
                        <span
                            className={cn(
                                "text-xs font-medium",
                                trend === "up" && "text-emerald-500",
                                trend === "down" && "text-red-500",
                                trend === "neutral" && "text-muted-foreground"
                            )}
                            aria-label={trend !== "neutral" ? `${trend} by ${change}` : change}
                        >
                            {change}
                        </span>
                    )}
                    {description && (
                        <span className="text-[10px] text-muted-foreground ml-1 italic">{description}</span>
                    )}
                </div>
            </CardContent>
        </Card>
    )
}
