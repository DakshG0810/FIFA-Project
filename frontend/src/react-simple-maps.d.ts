declare module "react-simple-maps" {
  import { ComponentType, ReactNode } from "react"

  export interface Geography {
    rsmKey: string
    properties: Record<string, unknown>
    [key: string]: unknown
  }

  export const ComposableMap: ComponentType<{
    projection?: string
    projectionConfig?: Record<string, unknown>
    width?: number
    height?: number
    style?: React.CSSProperties
    children?: ReactNode
  }>

  export const ZoomableGroup: ComponentType<{ zoom?: number; children?: ReactNode }>

  export const Geographies: ComponentType<{
    geography: string | object
    children: (props: { geographies: Geography[] }) => ReactNode
  }>

  export const Geography: ComponentType<{
    geography: Geography
    onMouseEnter?: () => void
    onMouseLeave?: () => void
    style?: Record<string, React.CSSProperties>
  }>

  export const Marker: ComponentType<{
    coordinates: [number, number]
    onMouseEnter?: () => void
    onMouseLeave?: () => void
    children?: ReactNode
  }>
}
