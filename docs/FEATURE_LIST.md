# Apache NAT (National Analytical Tool) Feature List

Apache NAT (National Analytical Tool) is a modern, enterprise-ready business intelligence web application. It is fast, lightweight, intuitive, and loaded with options that make it easy for users of all skill sets to explore and visualize their data, from simple pie charts to highly detailed geospatial charts.

## 🔮 Dashboards

Interactive and customizable dashboards are at the heart of the NAT (National Analytical Tool) experience.

- **Intuitive Interface**: Drag-and-drop interface for creating and resizing charts on a grid-based layout.
- **Rich Chart & Content Variety**: Dashboards can contain a wide array of visualizations as well as markdown content.
- **Native Filtering**: A powerful, built-in filtering component allows for sophisticated data filtering on dashboards.
- **Customizable UI**: Users can customize dashboard color schemes to match their organization's branding.
- **Auto-Refresh**: Dashboards can be configured to auto-refresh at a specified interval.
- **Embeddable Components**: NAT (National Analytical Tool) dashboards can be embedded in other applications.

## 📊 Explore (Charting)

The Explore view is a powerful and flexible interface for creating individual charts and exploring data.

- **No-Code Visualization Builder**: An intuitive UI allows users to create stunning visualizations without writing any code.
- **Wide Variety of Visualizations**: NAT (National Analytical Tool) supports a rich set of visualizations, from basic charts to complex geospatial analysis.
- **Semantic Layer**: A lightweight semantic layer allows for the definition of virtual metrics and calculated columns, enriching the data available for visualization.
- **Flexible Data Configuration**: Users can easily select datasources, metrics, dimensions, and apply filters to create the exact visualization they need.

### Available Chart Types

| Chart Type | Charts |
|---|---|
| **Time-series Charts** | Timeseries, Bar, Line, Scatter, Smooth Line, Step, Area, Mixed Timeseries, Horizon |
| **Categorical Charts** | Box Plot, Pie, Graph, Funnel, Sankey, Treemap, Tree, Sunburst, Waterfall, Rose, Partition, Chord, Parallel Coordinates |
| **Tabular Charts** | Table, Pivot Table, Time Table, AG Grid Table |
| **Geospatial Charts** | Country Map, World Map, MapBox, DeckGL (Arc, GeoJson, Grid, Hex, Heatmap, Multi, Path, Polygon, Scatter, Screengrid, Contour), Cartodiagram |
| **Other Charts** | Big Number, Big Number Total, Big Number Period Over Period, Bullet, Gauge, Radar, Histogram, Word Cloud, Paired T-Test, Calendar, Handlebars, Bubble, Legacy Bubble, Compare, Time Pivot, Heatmap |


## ✍️ SQL Lab

SQL Lab is a modern, multi-tab SQL IDE for data professionals.

- **Powerful SQL Editor**: A full-featured SQL editor with support for multiple tabs, allowing users to work on multiple queries at once.
- **Database Schema Browser**: Browse database schemas and tables within the editor.
- **Visualize Query Results**: Directly visualize query results in the Explore view.
- **Virtual Datasets**: Save query results as a "virtual dataset" to be used as a datasource for charting.

## 🔗 Data Connectivity

NAT (National Analytical Tool) can connect to any SQL-speaking database or data engine.

- **Broad Database Support**: Through SQLAlchemy, NAT (National Analytical Tool) supports a wide array of databases out of the box.
- **Easy Connection Management**: A simple UI for adding and configuring new database connections.
- **Custom Drivers**: Users can add custom database drivers to connect to any database with a Python DB-API driver.

## 🔐 Security & Access Control

NAT (National Analytical Tool) provides a robust and granular security model.

- **Role-Based Access Control (RBAC)**: A flexible security model that allows administrators to define granular permissions for users and roles.
- **Row-Level Security (RLS)**: A powerful feature that allows for defining rules to control access to data at the row level.
- **Integration with Authentication Backends**: NAT (National Analytical Tool) can be integrated with major authentication backends (database, OpenID, LDAP, OAuth, REMOTE_USER, etc).

## 🏗️ Architecture & Integration

NAT (National Analytical Tool) is built on a modern, extensible, and scalable architecture.

- **Cloud-Native Architecture**: NAT (National Analytical Tool) is designed to be highly available and scalable, and can be deployed in a variety of environments, including containerized environments like Kubernetes.
- **Extensible Platform**: A pluggable architecture allows for custom visualizations and other extensions.
- **Asynchronous Query Execution**: A message queue is used to handle long-running queries asynchronously, improving user experience.
- **Caching**: A configurable caching layer is used to improve performance and reduce database load.
- **Feature Flags**: A feature flag system allows for the safe rollout of new features.
- **REST API**: A public REST API for programmatic access to NAT (National Analytical Tool)'s functionality.
