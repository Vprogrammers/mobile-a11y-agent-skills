plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.kmp.library)
    alias(libs.plugins.compose.compiler)
}

kotlin {
    android {
        namespace = "dev.vprogrammers.a11y.kmp"
        compileSdk = 37
        minSdk = 24

        withHostTestBuilder {}.configure {
            isIncludeAndroidResources = true
        }
    }

    listOf(iosX64(), iosArm64(), iosSimulatorArm64()).forEach { target ->
        target.binaries.framework {
            baseName = "A11yShared"
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
        }
        commonTest.dependencies {
            implementation(kotlin("test"))
            implementation(libs.kotlinx.coroutines.test)
        }
        androidMain.dependencies {
            implementation(project.dependencies.platform(libs.compose.bom))
            implementation(libs.compose.ui)
        }
        getByName("androidHostTest").dependencies {
            implementation(project.dependencies.platform(libs.compose.bom))
            implementation(libs.compose.foundation)
            implementation(libs.compose.ui.test.junit4)
            implementation(libs.compose.ui.test.manifest)
            implementation(libs.activity.compose)
            implementation(libs.junit)
            implementation(libs.robolectric)
            implementation(libs.androidx.test.core)
        }
    }
}

// Compose is only the Android UI layer here; iOS uses native SwiftUI/UIKit, so it has no Compose runtime.
composeCompiler {
    targetKotlinPlatforms.set(setOf(org.jetbrains.kotlin.gradle.plugin.KotlinPlatformType.androidJvm))
}

/**
 * Swift consumers see the Objective-C header, not the Kotlin source. This check fails when the
 * exported shared API loses its platform-neutral contract or leaks UIKit or Compose types.
 */
abstract class CheckExportedHeader : DefaultTask() {
    @get:InputDirectory
    abstract val framework: DirectoryProperty

    @TaskAction
    fun check() {
        // KDoc is copied into the header; scan declarations only.
        val header = framework.get().asFile.resolve("A11yShared.framework/Headers/A11yShared.h").readText()
            .replace(Regex("""/\*.*?\*/""", RegexOption.DOT_MATCHES_ALL), "")
        val required = listOf("ValidationState", "messageKey", "isBlocking", "AccessibilityPreferences", "MotionPolicy")
        val missing = required.filterNot { it in header }
        check(missing.isEmpty()) { "Exported header is missing $missing" }
        val leaked = Regex("""\bUI[A-Z]\w+|Semantics|androidx""").findAll(header).map { it.value }.toSet()
        check(leaked.isEmpty()) { "Exported header leaks platform UI types: $leaked" }
    }
}

// Link for the simulator architecture of the host so the check runs on Intel and Apple silicon Macs.
val hostSimulator = if (System.getProperty("os.arch") == "aarch64") "IosSimulatorArm64" else "IosX64"
val linkHostFramework = tasks.named("linkDebugFramework$hostSimulator")

val checkExportedHeader = tasks.register<CheckExportedHeader>("checkExportedHeader") {
    framework.fileProvider(linkHostFramework.map { it.outputs.files.singleFile })
}

tasks.named("check") {
    dependsOn(checkExportedHeader)
}
