import SwiftUI

enum Space { static let s1: CGFloat = 4; static let s2: CGFloat = 8; static let s3: CGFloat = 12
             static let s4: CGFloat = 16; static let s6: CGFloat = 24; static let s8: CGFloat = 32 }
enum TypeScale {
    static let meta = Font.footnote                       // 13
    static let body = Font.body                           // 17
    static let hero = Font.system(size: 48, weight: .semibold).monospacedDigit()
}
enum Ink {
    static let primary = Color.primary
    static let secondary = Color("InkSecondary")          // #6C6C70 light / #AEAEB2 dark: 5.1:1 and 7.9:1
    static let soon = Color("InkSoon")                    // #A0520A light / #FFB25B dark: 5.6:1 and 9.4:1
}
enum Size { static let monogram: CGFloat = 32 }
