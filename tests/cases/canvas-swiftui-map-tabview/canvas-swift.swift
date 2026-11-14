struct ExploreView: View {
    var body: some View {
        TabView { Map(position: $pos).tabItem { Label("Map", systemImage: "map") } }
    }
}
