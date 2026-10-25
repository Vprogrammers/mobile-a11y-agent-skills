Fix the accessibility defects in `src/main/kotlin/evals/fixtures/OrderCard.kt` in this Gradle project.

TalkBack, Switch Access, and keyboard users must be able to use every action in `OrderCard` and understand every error in `AddressForm`. Keep the public function signatures and the existing behavior, including opening an order, tracking it, and editing the street. Do not add dependencies.

Build with `./gradlew --console=plain assembleDebug` before you finish, and report what you changed and what still needs a real-device check.
