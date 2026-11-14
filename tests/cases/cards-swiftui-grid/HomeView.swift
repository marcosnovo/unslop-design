import SwiftUI
struct HomeView: View {
  var body: some View {
    LazyVGrid(columns: [GridItem(), GridItem()]) {
      StatCard(title: "Steps", value: "8,204")
      StatCard(title: "Calories", value: "512")
      StatCard(title: "Distance", value: "6.8 km")
      StatCard(title: "Minutes", value: "39")
    }
  }
}
struct StatCard: View { let title: String; let value: String
  var body: some View { VStack { Text(title); Text(value) } } }
