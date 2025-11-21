`timescale 1ns/1ps

module cpu_tb;
    reg clk = 1'b0;
    reg rst = 1'b1;

    wire [31:0] pc_value;
    wire        parity_error;
    integer     cycle_count = 0;

    cpu_top dut (
        .clk         (clk),
        .rst         (rst),
        .pc_value    (pc_value),
        .parity_error(parity_error)
    );

    // Clock generation
    always #5 clk = ~clk;

    initial begin
        $display("Starting tinyml_risc_cpu simulation");
        #20 rst = 1'b0;
    end

    task automatic display_registers;
        integer i;
        begin
            $display("Register file snapshot:");
            for (i = 0; i < 16; i = i + 1) begin
                if (i % 4 == 0) begin
                    $write("   ");
                end
                $write("R%0d=%h ", i, dut.regfile_i.regs[i]);
                if (i % 4 == 3) begin
                    $display("");
                end
            end
            $display("");
        end
    endtask

    always @(posedge clk) begin
        if (rst) begin
            cycle_count <= 0;
            $display("[RESET] PC=%0d", pc_value);
        end else begin
            cycle_count <= cycle_count + 1;
            $display("---- Cycle %0d ----", cycle_count);
            $display("PC=%0d (0x%08h) INSTR=0x%08h OPCODE=0x%1h", pc_value, pc_value, dut.instruction, dut.opcode);
            $display("ALU=%0d (0x%08h) PARITY_ERR=%b", $signed(dut.alu_result), dut.alu_result, parity_error);
            $display("Operands: RS1=R%0d %0d (0x%08h)  RS2=R%0d %0d (0x%08h)", dut.rs1, $signed(dut.rs1_data), dut.rs1_data, dut.rs2, $signed(dut.rs2_data), dut.rs2_data);
            $display("Accumulator state: curr=%0d next_if_acc=%0d", $signed(dut.acc), $signed(dut.acc + (dut.opcode == 4'b1111 ? dut.rs1_data : 32'd0)));
            $display("TRACE cycle=%0d pc=%0d opcode=%0h alu=%0d acc=%0d rs1=%0d rs2=%0d", cycle_count, pc_value, dut.opcode, $signed(dut.alu_result), $signed(dut.acc), $signed(dut.rs1_data), $signed(dut.rs2_data));
            display_registers();

            if (dut.opcode == 4'b1000) begin
                $display("   -> MAC4 executing: result=%0d (0x%08h)", $signed(dut.alu_result), dut.alu_result);
            end
            if (dut.opcode == 4'b1101) begin
                $display("   -> CONV3 r%0d=%0d r%0d=%0d result=%0d", dut.rs1, $signed(dut.rs1_data), dut.rs2, $signed(dut.rs2_data), $signed(dut.alu_result));
            end
            if (dut.opcode == 4'b1110) begin
                $display("   -> SIGMOID input=%0d output=%0d (0x%02h)", $signed(dut.rs1_data), $signed(dut.alu_result[7:0]), dut.alu_result[7:0]);
            end
            if (dut.opcode == 4'b1111) begin
                $display("   -> ACC input=R%0d=%0d accum_before=%0d accum_after=%0d", dut.rs1, $signed(dut.rs1_data), $signed(dut.acc), $signed(dut.acc + dut.rs1_data));
            end

            if (pc_value >= 32'd80) begin
                $display("Program complete.");
                $display("   MAC4 result  : R3=%0d (0x%08h)", $signed(dut.regfile_i.regs[3]), dut.regfile_i.regs[3]);
                $display("   CONV3 result : R6=%0d (0x%08h)", $signed(dut.regfile_i.regs[6]), dut.regfile_i.regs[6]);
                $display("   SIGMOID (+)  : R8=%0d (0x%08h)", $signed(dut.regfile_i.regs[8][7:0]), dut.regfile_i.regs[8]);
                $display("   SIGMOID (-)  : R10=%0d (0x%08h)", $signed(dut.regfile_i.regs[10][7:0]), dut.regfile_i.regs[10]);
                $display("   ACC final    : %0d (0x%08h)", $signed(dut.acc), dut.acc);
                $finish;
            end
        end
    end

    initial begin
        #500;
        $display("Timeout - terminating simulation");
        $finish;
    end
endmodule
