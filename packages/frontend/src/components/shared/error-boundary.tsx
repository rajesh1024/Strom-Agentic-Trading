"use client"

import * as React from "react"
import { AlertCircle, RotateCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"

export interface ErrorBoundaryProps {
    children: React.ReactNode
    fallback?: React.ReactNode
    onReset?: () => void
}

interface ErrorBoundaryState {
    hasError: boolean
    error: Error | null
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
    constructor(props: ErrorBoundaryProps) {
        super(props)
        this.state = { hasError: false, error: null }
    }

    static getDerivedStateFromError(error: Error): ErrorBoundaryState {
        return { hasError: true, error }
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        console.error("ErrorBoundary caught an error", error, errorInfo)
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null })
        this.props.onReset?.()
    }

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback
            }

            return (
                <div className="flex h-full min-h-[400px] w-full items-center justify-center p-6 animate-in fade-in zoom-in duration-300">
                    <Card className="max-w-md border-destructive/20 bg-destructive/5 backdrop-blur shadow-2xl shadow-destructive/10">
                        <CardHeader className="flex flex-col items-center gap-3 text-center pb-2">
                            <div className="p-3 bg-destructive/10 rounded-full">
                                <AlertCircle className="size-8 text-destructive" />
                            </div>
                            <CardTitle className="text-xl font-bold tracking-tight">Component Failed to Load</CardTitle>
                        </CardHeader>
                        <CardContent className="text-center text-muted-foreground">
                            <p className="text-sm">
                                An error occurred while rendering this component. Our team has been notified.
                            </p>
                            {process.env.NODE_ENV === "development" && this.state.error && (
                                <div className="mt-4 p-3 bg-muted rounded-md text-left overflow-auto max-h-[150px]">
                                    <code className="text-[11px] text-destructive leading-tight whitespace-pre-wrap">
                                        {this.state.error.toString()}
                                    </code>
                                </div>
                            )}
                        </CardContent>
                        <CardFooter className="flex justify-center border-t border-destructive/10 mt-2">
                            <Button
                                variant="outline"
                                onClick={this.handleReset}
                                className="gap-2 mt-4 hover:bg-destructive/10 hover:text-destructive border-border"
                            >
                                <RotateCcw className="size-4" />
                                Try Re-rendering
                            </Button>
                        </CardFooter>
                    </Card>
                </div>
            )
        }

        return this.props.children
    }
}

export function ErrorBoundaryWrapper({ children, ...props }: ErrorBoundaryProps) {
    return <ErrorBoundary {...props}>{children}</ErrorBoundary>
}
