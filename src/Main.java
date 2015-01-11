import lejos.nxt.*;
import lejos.nxt.comm.USB;
import lejos.robotics.navigation.DifferentialPilot;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.NXTSocketUtils;
import java.net.Socket;

public class Main {
    private static final int JAWS_OPEN = -30;

    private static NXTRegulatedMotor jawMotor = Motor.C;
    private static ButtonListener stop = new ButtonListener() {
        public void buttonPressed(Button b) {
            System.exit(0);
        }

        public void buttonReleased(Button b) {

        }
    };

    private static void resetJaws() {
        jawMotor.setAcceleration((int)(jawMotor.getMaxSpeed() * 2.0f));
        jawMotor.setStallThreshold(50, 100);
        jawMotor.setSpeed(jawMotor.getMaxSpeed() / 2.0f);

        jawMotor.forward();
        //noinspection StatementWithEmptyBody
        while (!jawMotor.isStalled()) {
        }
        jawMotor.stop();

        jawMotor.resetTachoCount();
        jawMotor.backward();
        //noinspection StatementWithEmptyBody
        while (jawMotor.getTachoCount() > JAWS_OPEN) {
        }
        jawMotor.stop();
    }

    private static void closeJaws() {
        jawMotor.rotateTo(-115, true);
    }

    private static void openJaws() {
        jawMotor.rotateTo(0, true);
    }

    public static void main(String[] args) throws IOException {
        for (Button button : Button.BUTTONS) {
            button.addButtonListener(stop);
        }
        resetJaws();

        while (true) {
            System.out.println("Waiting for USB");
            NXTSocketUtils.setNXTConnection(USB.waitForConnection());
            System.out.println("USB connected.");
            Socket sock = new Socket("localhost", 9001);

            DataInputStream dataInputStream = new DataInputStream(sock.getInputStream());

            DifferentialPilot diffPilot = new DifferentialPilot(56.0f, 2200.0f, Motor.B, Motor.A);
//            Motor.A.setStallThreshold(50000000, 100000);
//            Motor.B.setStallThreshold(50000000, 100000);

            double travelSpeed = diffPilot.getMaxTravelSpeed() / 3.0f;
            diffPilot.setTravelSpeed(travelSpeed);
            diffPilot.setAcceleration((int) (diffPilot.getMaxTravelSpeed() * 5.0f));
            //noinspection InfiniteLoopStatement
            int num = 0;
            while (true) {
                int b;
                try {
                    b = dataInputStream.readUnsignedByte();
                } catch (Exception e) {
                    diffPilot.stop();
                    System.out.println("Disconnected.");
                    break;
                }
//                System.out.print(num++);
//                System.out.print(' ');
//                System.out.println((char) b);
                switch (b) {
                    case ' ':
                        Motor.A.flt(true);
                        Motor.B.flt(true);
                        break;
                    case ',':
                        diffPilot.forward();
                        break;
                    case 'o':
                        diffPilot.backward();
                        break;
                    case 'a':
                        diffPilot.steer(200.0);
                        break;
                    case 'e':
                        diffPilot.steer(-200.0);
                        break;
                    case 'q':
                        System.exit(0);
                        break;
                    case '1':
                        travelSpeed = diffPilot.getMaxTravelSpeed() / 3.0f;
                        diffPilot.setTravelSpeed(travelSpeed);
                        break;
                    case '2':
                        travelSpeed = diffPilot.getMaxTravelSpeed() * 0.7f;
                        diffPilot.setTravelSpeed(travelSpeed);
                        break;
                    case '3':
                        travelSpeed = diffPilot.getMaxTravelSpeed() / 1.0f;
                        diffPilot.setTravelSpeed(travelSpeed);
                        break;
                    case 'b':
                        Sound.beep();
                        break;
                    case 'r':
                        resetJaws();
                        break;
                    case '+':
                        closeJaws();
                        break;
                    case '-':
                        openJaws();
                        break;
                    default:
                        if (b >= 'A' && b <= 'Z') {
                            int n = b - 'A';
                            int steer = n / 2;
                            int sign = n % 2;
                            diffPilot.steer(steer * 10 * (sign == 0 ? 1 : -1));
                        }
                }
            }
        }
    }

}
