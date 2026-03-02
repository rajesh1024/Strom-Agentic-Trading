import { render, screen } from "@testing-library/react"
import { DataTable } from "@/components/shared/data-table"
import { describe, it, expect } from "vitest"
import { ColumnDef } from "@tanstack/react-table"

type TestData = {
    id: string
    name: string
    status: string
}

const columns: ColumnDef<TestData>[] = [
    { accessorKey: "name", header: "Name" },
    { accessorKey: "status", header: "Status" },
]

const data: TestData[] = [
    { id: "1", name: "Alpha", status: "Active" },
    { id: "2", name: "Beta", status: "Inactive" },
]

describe("DataTable", () => {
    it("renders headers and data correctly", () => {
        render(<DataTable columns={columns} data={data} />)
        expect(screen.getByText("Name")).toBeInTheDocument()
        expect(screen.getByText("Status")).toBeInTheDocument()
        expect(screen.getByText("Alpha")).toBeInTheDocument()
        expect(screen.getByText("Beta")).toBeInTheDocument()
    })

    it("shows empty state when no data is provided", () => {
        render(<DataTable columns={columns} data={[]} />)
        expect(screen.getByText("No results found matching your search.")).toBeInTheDocument()
    })
})
